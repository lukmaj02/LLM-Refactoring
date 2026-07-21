# === ARP Faza 4C - refactored code ===
# sample_id: requests_035
# condition: A
# timestamp: 2026-06-04T13:57:29
# original_cc: 1, original_mi: None
# changed_pct: 0.7778
# === END HEADER ===
def delete(self, url, **kwargs):
    return self.request("DELETE", url, **kwargs)