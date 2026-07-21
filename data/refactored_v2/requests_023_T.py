# === ARP Faza 4C - refactored code ===
# sample_id: requests_023
# condition: T
# timestamp: 2026-06-04T13:44:40
# original_cc: 6, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def get_dict(self, domain=None, path=None):
    """Takes as an argument an optional domain and path and returns a plain
    old Python dict of name-value pairs of cookies that meet the
    requirements.

    :rtype: dict
    """
    dictionary = {}
    for cookie in iter(self):
        if (domain is None or cookie.domain == domain) and (
            path is None or cookie.path == path
        ):
            dictionary[cookie.name] = cookie.value
    return dictionary
