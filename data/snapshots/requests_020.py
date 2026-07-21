# SNAPSHOT METADATA
# sample_id: requests_020
# repo: requests
# file: data/repos/requests/src/requests/models.py
# function: RequestHooksMixin.register_hook
# cc: 6 | mi: N/A | loc: 10
# extracted: 2026-05-01T11:47:36

def register_hook(self, event, hook):
    """Properly register a hook."""

    if event not in self.hooks:
        raise ValueError(f'Unsupported event specified, with event name "{event}"')

    if isinstance(hook, Callable):
        self.hooks[event].append(hook)
    elif hasattr(hook, "__iter__"):
        self.hooks[event].extend(h for h in hook if isinstance(h, Callable))
