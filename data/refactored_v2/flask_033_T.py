# === ARP Faza 4C - refactored code ===
# sample_id: flask_033
# condition: T
# timestamp: 2026-06-04T14:12:26
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __init__(
    self,
    initial: c.Mapping[str, t.Any] | None = None,
) -> None:
    def on_update(self: te.Self) -> None:
        self.modified = True

    super().__init__(initial, on_update)
