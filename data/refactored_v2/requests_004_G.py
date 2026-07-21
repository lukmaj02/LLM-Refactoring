# === ARP Faza 4C - refactored code ===
# sample_id: requests_004
# condition: G
# timestamp: 2026-06-04T13:24:09
# original_cc: 19, original_mi: None
# changed_pct: 0.9817
# === END HEADER ===
class HTTPDigestAuth(AuthBase):
    """Attaches HTTP Digest Authentication to the given Request object."""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        # Keep state in per-thread local storage
        self._thread_local = threading.local()

    def init_per_thread_state(self):
        # Ensure state is initialized just once per-thread
        if not hasattr(self._thread_local, "init"):
            self._thread_local.init = True
            self._thread_local.last_nonce = ""
            self._thread_local.nonce_count = 0
            self._thread_local.chal = {}
            self._