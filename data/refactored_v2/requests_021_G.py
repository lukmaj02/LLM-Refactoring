# === ARP Faza 4C - refactored code ===
# sample_id: requests_021
# condition: G
# timestamp: 2026-06-04T13:39:00
# original_cc: 7, original_mi: None
# changed_pct: 0.3889
# === END HEADER ===
def _get_default_mutable_param(value, default_factory):
    """Returns value if not None, otherwise returns the result of default_factory()."""
    return value if value is not None else default_factory()

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
    # Default empty dicts/lists for mutable parameters if None is provided.
    self.data = _get_default_mutable_param(data, list)
    self.files = _get_default_mutable_param(files, list)
    self.headers = _get_default_mutable_param(headers, dict)
    self.params = _get_default_mutable_param(params, dict)
    
    # The 'hooks' parameter is used to extend/override default_hooks,
    # not to directly set self.hooks.
    init_hooks_param = _get_default_mutable_param(hooks, dict)

    self.hooks = default_hooks()
    for k, v in list(init_hooks_param.items()):
        self.register_hook(event=k, hook=v)

    self.method = method
    self.url = url
    self.json = json
    self.auth = auth
    self.cookies = cookies