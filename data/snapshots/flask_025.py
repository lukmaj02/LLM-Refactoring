# SNAPSHOT METADATA
# sample_id: flask_025
# repo: flask
# file: data/repos/flask/src/flask/ctx.py
# function: AppContext.__init__
# cc: 1 | mi: N/A | loc: 5
# extracted: 2026-05-01T11:47:37

def __init__(self, app: Flask) -> None:
    self.app = app
    self.url_adapter = app.create_url_adapter(None)
    self.g: _AppCtxGlobals = app.app_ctx_globals_class()
    self._cv_tokens: list[contextvars.Token[AppContext]] = []
