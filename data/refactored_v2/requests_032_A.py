# === ARP Faza 4C - refactored code ===
# sample_id: requests_032
# condition: A
# timestamp: 2026-06-04T13:53:09
# original_cc: 4, original_mi: None
# changed_pct: 0.4615
# === END HEADER ===
def multiple_domains(self):
    """Returns True if there are multiple domains in the jar.
    Returns False otherwise.

    :rtype: bool
    """
    seen_domains = set()
    for cookie in iter(self):
        if cookie.domain is not None:
            if cookie.domain in seen_domains:
                return True
            seen_domains.add(cookie.domain)
    return False