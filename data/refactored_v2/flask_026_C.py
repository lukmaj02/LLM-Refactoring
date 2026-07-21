# === ARP Faza 4C - refactored code ===
# sample_id: flask_026
# condition: C
# timestamp: 2026-06-04T14:17:57
# original_cc: 2, original_mi: None
# changed_pct: 0.1667
# === END HEADER ===
@debug.setter
def debug(self, value: bool) -> None:
    self.config["DEBUG"] = value

    if self.config["TEMPLATES_AUTO_RELOAD"] is None:
        self.jinja_env.auto_reload = value