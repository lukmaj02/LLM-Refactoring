# === ARP Faza 4C - refactored code ===
# sample_id: flask_026
# condition: A
# timestamp: 2026-06-04T14:16:54
# original_cc: 2, original_mi: None
# changed_pct: 0.2857
# === END HEADER ===
def debug(self, value: bool) -> None:
    self.config["DEBUG"] = value
    self._set_auto_reload(value)

def _set_auto_reload(self, value: bool) -> None:
    if self.config["TEMPLATES_AUTO_RELOAD"] is None:
        self.jinja_env.auto_reload = value