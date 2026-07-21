# === ARP Faza 4C - refactored code ===
# sample_id: flask_033
# condition: G
# timestamp: 2026-06-04T14:22:29
# original_cc: 1, original_mi: None
# changed_pct: 0.5000
# === END HEADER ===
def __init__(
    self,
    initial: c.Mapping[str, t.Any] | None = None,
) -> None:
    super().__init__(initial, on_update=lambda self_dict: setattr(self_dict, "modified", True))