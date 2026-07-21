# === ARP Faza 4C - refactored code ===
# sample_id: httpie_006
# condition: G
# timestamp: 2026-06-04T13:58:59
# original_cc: 12, original_mi: None
# changed_pct: 0.5641
# === END HEADER ===
def _is_user_agent_to_ignore(self, name: str, value: str) -> bool:
    return name.lower() == 'user-agent' and value.startswith('HTTPie/')

def _is_header_ignored_by_prefix(self, name: str) -> bool:
    for prefix in SESSION_IGNORED_HEADER_PREFIXES:
        if name.lower().startswith(prefix.lower()):
            return True
    return False

def _handle_cookie_header(self, name: str, value: str, original_value: Any, request_headers: HTTPHeadersDict) -> None:
    for cookie_name, morsel in SimpleCookie(value).items():
        if not morsel['path']:
            morsel['path'] = DEFAULT_COOKIE_PATH
        self.cookie_jar.set(cookie_name, morsel)
    request_headers.remove_item(name, original_value)

def _compute_new_headers(self, request_headers: HTTPHeadersDict) -> HTTPHeadersDict:
    new_headers = HTTPHeadersDict()
    for name, value in request_headers.copy().items():
        if value is None:
            continue  # Ignore explicitly unset headers

        original_value = value
        if type(value) is not str:
            value = value.decode()

        if self._is_user_agent_to_ignore(name, value):
            continue

        if name.lower() == 'cookie':
            self._handle_cookie_header(name, value, original_value, request_headers)
            continue

        if self._is_header_ignored_by_prefix(name):
            continue

        new_headers.add(name, value)

    return new_headers