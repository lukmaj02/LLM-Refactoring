# === ARP Faza 4C - refactored code ===
# sample_id: httpie_006
# condition: C
# timestamp: 2026-06-04T14:00:40
# original_cc: 12, original_mi: None
# changed_pct: 0.5405
# === END HEADER ===
def _is_default_user_agent(self, name, value):
    return name.lower() == 'user-agent' and value.startswith('HTTPie/')


def _is_ignored_prefix(self, name):
    return any(name.lower().startswith(prefix.lower()) for prefix in SESSION_IGNORED_HEADER_PREFIXES)


def _handle_cookie_header(self, name, original_value, value, request_headers):
    for cookie_name, morsel in SimpleCookie(value).items():
        if not morsel['path']:
            morsel['path'] = DEFAULT_COOKIE_PATH
        self.cookie_jar.set(cookie_name, morsel)
    request_headers.remove_item(name, original_value)


def _compute_new_headers(self, request_headers: HTTPHeadersDict) -> HTTPHeadersDict:
    new_headers = HTTPHeadersDict()
    for name, value in request_headers.copy().items():
        if value is None:
            continue

        original_value = value
        if type(value) is not str:
            value = value.decode()

        if self._is_default_user_agent(name, value):
            continue

        if name.lower() == 'cookie':
            self._handle_cookie_header(name, original_value, value, request_headers)
            continue

        if not self._is_ignored_prefix(name):
            new_headers.add(name, value)

    return new_headers