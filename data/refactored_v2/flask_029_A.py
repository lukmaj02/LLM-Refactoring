# === ARP Faza 4C - refactored code ===
# sample_id: flask_029
# condition: A
# timestamp: 2026-06-04T14:17:53
# original_cc: 2, original_mi: None
# changed_pct: 0.8000
# === END HEADER ===
def static_folder(self, value: str | os.PathLike[str] | None) -> None:
    self._static_folder = os.fspath(value).rstrip(r"\/") if value is not None else value