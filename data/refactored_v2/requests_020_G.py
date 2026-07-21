# === ARP Faza 4C - refactored code ===
# sample_id: requests_020
# condition: G
# timestamp: 2026-06-04T13:37:44
# original_cc: 6, original_mi: None
# changed_pct: 0.8667
# === END HEADER ===
class RequestHooksMixin:
    def _extend_hooks_from_iterable(self, event, hooks_iterable):
        """Helper to extend the hooks list with callable items from an iterable."""
        self.hooks[event].extend(h for h in hooks_iterable if isinstance(h, Callable))

    def register_hook(self, event, hook):
        """Properly register a hook."""

        if event not in self.hooks:
            raise ValueError(f'Unsupported event specified, with event name "{event}"')

        if isinstance(hook, Callable):
            self.hooks[event].append(hook)
        elif hasattr(hook, "__iter__"):
            self._extend_hooks_from_iterable(event, hook)