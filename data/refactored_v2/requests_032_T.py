# === ARP Faza 4C - refactored code ===
# sample_id: requests_032
# condition: T
# timestamp: 2026-06-04T13:55:31
# original_cc: 4, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
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
