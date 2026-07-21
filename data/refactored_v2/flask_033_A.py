# === ARP Faza 4C - refactored code ===
# sample_id: flask_033
# condition: A
# timestamp: 2026-06-04T14:18:47
# original_cc: 1, original_mi: None
# changed_pct: 0.3750
# === END HEADER ===
def __init__(
    self,
    initial: c.Mapping[str, t.Any] | None = None,
) -> None:
    super().__init__(initial, self._on_update)

def _on_update(self: te.Self) -> None:
    self.modified = True