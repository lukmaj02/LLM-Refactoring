# === ARP Faza 4C - refactored code ===
# sample_id: requests_024
# condition: T
# timestamp: 2026-06-04T13:45:53
# original_cc: 7, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
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
