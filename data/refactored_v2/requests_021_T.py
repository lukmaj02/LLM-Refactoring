# === ARP Faza 4C - refactored code ===
# sample_id: requests_021
# condition: T
# timestamp: 2026-06-04T13:42:11
# original_cc: 7, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __init__(
    self,
    method=None,
    url=None,
    headers=None,
    files=None,
    data=None,
    params=None,
    auth=None,
    cookies=None,
    hooks=None,
    json=None,
):
    # Default empty dicts for dict params.
    data = [] if data is None else data
    files = [] if files is None else files
    headers = {} if headers is None else headers
    params = {} if params is None else params
    hooks = {} if hooks is None else hooks

    self.hooks = default_hooks()
    for k, v in list(hooks.items()):
        self.register_hook(event=k, hook=v)

    self.method = method
    self.url = url
    self.headers = headers
    self.files = files
    self.data = data
    self.json = json
    self.params = params
    self.auth = auth
    self.cookies = cookies
