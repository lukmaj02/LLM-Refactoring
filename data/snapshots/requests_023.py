# SNAPSHOT METADATA
# sample_id: requests_023
# repo: requests
# file: data/repos/requests/src/requests/cookies.py
# function: RequestsCookieJar.get_dict
# cc: 6 | mi: N/A | loc: 14
# extracted: 2026-05-01T11:47:36

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
