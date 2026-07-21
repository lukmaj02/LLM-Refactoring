# === ARP Faza 4C - refactored code ===
# sample_id: flask_026
# condition: G
# timestamp: 2026-06-04T14:20:56
# original_cc: 2, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def debug(self, value: bool) -> None:
    self.config["DEBUG"] = value

    if self.config["TEMPLATES_AUTO_RELOAD"] is None:
        self.jinja_env.auto_reload = value