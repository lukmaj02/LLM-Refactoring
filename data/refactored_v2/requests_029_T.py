# === ARP Faza 4C - refactored code ===
# sample_id: requests_029
# condition: T
# timestamp: 2026-06-04T13:52:06
# original_cc: 2, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __setstate__(self, state):
    # Can't handle by adding 'proxy_manager' to self.__attrs__ because
    # self.poolmanager uses a lambda function, which isn't pickleable.
    self.proxy_manager = {}
    self.config = {}

    for attr, value in state.items():
        setattr(self, attr, value)

    self.init_poolmanager(
        self._pool_connections, self._pool_maxsize, block=self._pool_block
    )
