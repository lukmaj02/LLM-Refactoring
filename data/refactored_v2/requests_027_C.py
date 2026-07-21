# === ARP Faza 4C - refactored code ===
# sample_id: requests_027
# condition: C
# timestamp: 2026-06-04T13:48:26
# original_cc: 1, original_mi: None
# changed_pct: 0.6739
# === END HEADER ===
def __init__(self):
    self._content = False
    self._content_consumed = False
    self._next = None

    self.status_code = None
    self.headers = CaseInsensitiveDict()
    self.raw = None
    self.url = None
    self.encoding = None
    self.history = []
    self.reason = None
    self.cookies = cookiejar_from_dict({})
    self.elapsed = datetime.timedelta(0)
    self.request = None