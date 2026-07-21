# === ARP Faza 4C - refactored code ===
# sample_id: httpie_030
# condition: A
# timestamp: 2026-06-04T14:09:02
# original_cc: 1, original_mi: None
# changed_pct: 0.3000
# === END HEADER ===
def __init__(self, env):
    self.env = env
    self._initialize_status()

def _initialize_status(self):
    self.downloaded = 0
    self.total_size = None
    self.resumed_from = 0
    self.time_started = None
    self.time_finished = None