# === ARP Faza 4C - refactored code ===
# sample_id: httpie_006
# condition: T
# timestamp: 2026-06-04T14:03:01
# original_cc: 12, original_mi: None
# changed_pct: 0.0968
# === END HEADER ===
def _compute_new_headers(
        self,
        request_headers: HTTPHeadersDict) -> HTTPHeadersDict:
    new_headers = HTTPHeadersDict()
    for name, value in request_headers.copy().items():
        if value is None:
            continue  # Ignore explicitly unset headers

        original_value = value
        if type(value) is not str:
            value = value.decode()

        if name.lower() == 'user-agent' and value.startswith('HTTPie/'):
            continue

        if name.lower() == 'cookie':
            for cookie_name, morsel in SimpleCookie(value).items():
                if not morsel['path']:
                    morsel['path'] = DEFAULT_COOKIE_PATH
                self.cookie_jar.set(cookie_name, morsel)

            request_headers.remove_item(name, original_value)
            continue

        for prefix in SESSION_IGNORED_HEADER_PREFIXES:
            if name.lower().startswith(prefix.lower()):
                break
        else:
            new_headers.add(name, value)

    return new_headers
