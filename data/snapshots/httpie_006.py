# SNAPSHOT METADATA
# sample_id: httpie_006
# repo: httpie
# file: data/repos/httpie/httpie/sessions.py
# function: Session._compute_new_headers
# cc: 12 | mi: N/A | loc: 29
# extracted: 2026-05-01T11:47:36

def _compute_new_headers(self, request_headers: HTTPHeadersDict) -> HTTPHeadersDict:
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
