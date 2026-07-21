# SNAPSHOT METADATA
# sample_id: requests_024
# repo: requests
# file: data/repos/requests/src/requests/cookies.py
# function: RequestsCookieJar._find
# cc: 7 | mi: N/A | loc: 19
# extracted: 2026-05-01T11:47:36

def _find(self, name, domain=None, path=None):
    """Requests uses this method internally to get cookie values.

    If there are conflicting cookies, _find arbitrarily chooses one.
    See _find_no_duplicates if you want an exception thrown if there are
    conflicting cookies.

    :param name: a string containing name of cookie
    :param domain: (optional) string containing domain of cookie
    :param path: (optional) string containing path of cookie
    :return: cookie.value
    """
    for cookie in iter(self):
        if cookie.name == name:
            if domain is None or cookie.domain == domain:
                if path is None or cookie.path == path:
                    return cookie.value

    raise KeyError(f"name={name!r}, domain={domain!r}, path={path!r}")
