# === ARP Faza 4C - refactored code ===
# sample_id: requests_021
# condition: A
# timestamp: 2026-06-04T13:39:46
# original_cc: 7, original_mi: None
# changed_pct: 0.3939
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
    self.data = data if data is not None else []
    self.files = files if files is not None else []
    self.headers = headers if headers is not None else {}
    self.params = params if params is not None else {}
    self.hooks = default_hooks()

    if hooks:
        self._register_hooks(hooks)

    self.method = method
    self.url = url
    self.json = json
    self.auth = auth
    self.cookies = cookies

def _register_hooks(self, hooks):
    for k, v in hooks.items():
        self.register_hook(event=k, hook=v)