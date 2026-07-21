# SNAPSHOT METADATA
# sample_id: requests_032
# repo: requests
# file: data/repos/requests/src/requests/cookies.py
# function: RequestsCookieJar.multiple_domains
# cc: 4 | mi: N/A | loc: 12
# extracted: 2026-05-01T11:47:36

def multiple_domains(self):
    """Returns True if there are multiple domains in the jar.
    Returns False otherwise.

    :rtype: bool
    """
    domains = []
    for cookie in iter(self):
        if cookie.domain is not None and cookie.domain in domains:
            return True
        domains.append(cookie.domain)
    return False  # there is only one domain in jar
