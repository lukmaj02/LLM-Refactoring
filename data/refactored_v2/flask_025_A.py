# === ARP Faza 4C - refactored code ===
# sample_id: flask_025
# condition: A
# timestamp: 2026-06-04T14:16:45
# original_cc: 1, original_mi: None
# changed_pct: 0.8182
# === END HEADER ===
def __init__(self, app: Flask) -> None:
    self.app = app
    self.url_adapter = self._create_url_adapter(app)
    self.g = self._create_app_ctx_globals(app)
    self._cv_tokens = []

def _create_url_adapter(app: Flask):
    return app.create_url_adapter(None)

def _create_app_ctx_globals(app: Flask) -> _AppCtxGlobals:
    return app.app_ctx_globals_class()