# === ARP Faza 4C - refactored code ===
# sample_id: requests_032
# condition: C
# timestamp: 2026-06-04T13:53:16
# original_cc: 4, original_mi: None
# changed_pct: 0.5000
# === END HEADER ===
def multiple_domains(self):
    """Returns True if there are multiple domains in the jar.
    Returns False otherwise.

    :rtype: bool
    """
    return len(set(self.list_domains())) > 1