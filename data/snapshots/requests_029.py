# SNAPSHOT METADATA
# sample_id: requests_029
# repo: requests
# file: data/repos/requests/src/requests/adapters.py
# function: HTTPAdapter.__setstate__
# cc: 2 | mi: N/A | loc: 11
# extracted: 2026-05-01T11:47:36

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
