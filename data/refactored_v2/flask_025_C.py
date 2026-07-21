# === ARP Faza 4C - refactored code ===
# sample_id: flask_025
# condition: C
# timestamp: 2026-06-04T14:17:49
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __init__(self, app: Flask) -> None:
    self.app = app
    self.url_adapter = app.create_url_adapter(None)
    self.g: _AppCtxGlobals = app.app_ctx_globals_class()
    self._cv_tokens: list[contextvars.Token[AppContext]] = []