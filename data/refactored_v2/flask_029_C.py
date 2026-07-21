# === ARP Faza 4C - refactored code ===
# sample_id: flask_029
# condition: C
# timestamp: 2026-06-04T14:19:06
# original_cc: 2, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def static_folder(self, value: str | os.PathLike[str] | None) -> None:
    if value is not None:
        value = os.fspath(value).rstrip(r"\/")

    self._static_folder = value