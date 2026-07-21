# === ARP Faza 4C - refactored code ===
# sample_id: requests_020
# condition: A
# timestamp: 2026-06-04T13:38:28
# original_cc: 6, original_mi: None
# changed_pct: 0.3846
# === END HEADER ===
def register_hook(self, event, hook):
    """Properly register a hook."""

    if event not in self.hooks:
        raise ValueError(f'Unsupported event specified, with event name "{event}"')

    hooks_to_add = []
    if isinstance(hook, Callable):
        hooks_to_add.append(hook)
    elif hasattr(hook, "__iter__"):
        hooks_to_add.extend(h for h in hook if isinstance(h, Callable))

    self.hooks[event].extend(hooks_to_add)