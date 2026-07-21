# === ARP Faza 4C - refactored code ===
# sample_id: httpie_006
# condition: A
# timestamp: 2026-06-04T14:00:16
# original_cc: 12, original_mi: None
# changed_pct: 0.5882
# === END HEADER ===
def _compute_new_headers(self, request_headers: HTTPHeadersDict) -> HTTPHeadersDict:
    new_headers = HTTPHeadersDict()
    for name, value in request_headers.copy().items():
        if value is None:
            continue  # Ignore explicitly unset headers

        value = self._decode_value(value)
        if self._is_ignored_user_agent(name, value):
            continue

        if name.lower() == 'cookie':
            self._process_cookie_header(name, value, request_headers)
            continue

        if not self._is_ignored_header(name):
            new_headers.add(name, value)

    return new_headers

def _decode_value(self, value):
    return value if isinstance(value, str) else value.decode()

def _is_ignored_user_agent(self, name, value):
    return name.lower() == 'user-agent' and value.startswith('HTTPie/')

def _process_cookie_header(self, name, value, request_headers):
    for cookie_name, morsel in SimpleCookie(value).items():
        if not morsel['path']:
            morsel['path'] = DEFAULT_COOKIE_PATH
        self.cookie_jar.set(cookie_name, morsel)
    request_headers.remove_item(name, value)

def _is_ignored_header(self, name):
    return any(name.lower().startswith(prefix.lower()) for prefix in SESSION_IGNORED_HEADER_PREFIXES)