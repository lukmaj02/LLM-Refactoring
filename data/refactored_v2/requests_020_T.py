# === ARP Faza 4C - refactored code ===
# sample_id: requests_020
# condition: T
# timestamp: 2026-06-04T13:40:33
# original_cc: 6, original_mi: None
# changed_pct: 0.1818
# === END HEADER ===
def register_hook(self, event, hook):
    """Properly register a hook."""

    if event not in self.hooks:
        raise ValueError(
            f'Unsupported event specified, with event name "{event}"')

    if isinstance(hook, Callable):
        self.hooks[event].append(hook)
    elif hasattr(hook, "__iter__"):
        self.hooks[event].extend(h for h in hook if isinstance(h, Callable))
