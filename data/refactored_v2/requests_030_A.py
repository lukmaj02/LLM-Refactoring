# === ARP Faza 4C - refactored code ===
# sample_id: requests_030
# condition: A
# timestamp: 2026-06-04T13:50:24
# original_cc: 2, original_mi: None
# changed_pct: 0.2609
# === END HEADER ===
def __init__(
    self,
    pool_connections=DEFAULT_POOLSIZE,
    pool_maxsize=DEFAULT_POOLSIZE,
    max_retries=DEFAULT_RETRIES,
    pool_block=DEFAULT_POOLBLOCK,
):
    self.max_retries = self._initialize_max_retries(max_retries)
    self.config = {}
    self.proxy_manager = {}

    super().__init__()

    self._pool_connections = pool_connections
    self._pool_maxsize = pool_maxsize
    self._pool_block = pool_block

    self.init_poolmanager(pool_connections, pool_maxsize, block=pool_block)

def _initialize_max_retries(self, max_retries):
    if max_retries == DEFAULT_RETRIES:
        return Retry(0, read=False)
    return Retry.from_int(max_retries)