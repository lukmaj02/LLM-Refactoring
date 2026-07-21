# === ARP Faza 4C - refactored code ===
# sample_id: requests_030
# condition: C
# timestamp: 2026-06-04T13:50:29
# original_cc: 2, original_mi: None
# changed_pct: 0.1905
# === END HEADER ===
def __init__(
    self,
    pool_connections=DEFAULT_POOLSIZE,
    pool_maxsize=DEFAULT_POOLSIZE,
    max_retries=DEFAULT_RETRIES,
    pool_block=DEFAULT_POOLBLOCK,
):
    self.max_retries = Retry(0, read=False) if max_retries == DEFAULT_RETRIES else Retry.from_int(max_retries)
    self.config = {}
    self.proxy_manager = {}

    super().__init__()

    self._pool_connections = pool_connections
    self._pool_maxsize = pool_maxsize
    self._pool_block = pool_block

    self.init_poolmanager(pool_connections, pool_maxsize, block=pool_block)