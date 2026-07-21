# === ARP Faza 4C - refactored code ===
# sample_id: flask_034
# condition: A
# timestamp: 2026-06-04T14:18:56
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __exit__(
    self,
    exc_type: type | None,
    exc_value: BaseException | None,
    tb: TracebackType | None,
) -> None:
    self.pop(exc_value)