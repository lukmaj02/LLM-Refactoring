# === ARP Faza 4C - refactored code ===
# sample_id: requests_029
# condition: A
# timestamp: 2026-06-04T13:49:57
# original_cc: 2, original_mi: None
# changed_pct: 0.5714
# === END HEADER ===
def __setstate__(self, state):
    self._reset_state()
    self._restore_state(state)
    self.init_poolmanager(
        self._pool_connections, self._pool_maxsize, block=self._pool_block
    )

def _reset_state(self):
    self.proxy_manager = {}
    self.config = {}

def _restore_state(self, state):
    for attr, value in state.items():
        setattr(self, attr, value)