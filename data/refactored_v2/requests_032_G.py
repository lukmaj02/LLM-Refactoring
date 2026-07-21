# === ARP Faza 4C - refactored code ===
# sample_id: requests_032
# condition: G
# timestamp: 2026-06-04T13:51:08
# original_cc: 4, original_mi: None
# changed_pct: 0.8667
# === END HEADER ===
def multiple_domains(self):
        """Returns True if there are multiple domains in the jar,
        specifically if any non-None domain appears more than once.
        Returns False otherwise.

        :rtype: bool
        """
        seen_non_none_domains = set()
        for cookie in iter(self):
            domain = cookie.domain
            if domain is not None:
                if domain in seen_non_none_domains:
                    return True
                seen_non_none_domains.add(domain)
        return False