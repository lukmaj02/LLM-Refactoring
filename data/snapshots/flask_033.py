# SNAPSHOT METADATA
# sample_id: flask_033
# repo: flask
# file: data/repos/flask/src/flask/sessions.py
# function: SecureCookieSession.__init__
# cc: 1 | mi: N/A | loc: 8
# extracted: 2026-05-01T11:47:37

def __init__(
    self,
    initial: c.Mapping[str, t.Any] | None = None,
) -> None:
    def on_update(self: te.Self) -> None:
        self.modified = True

    super().__init__(initial, on_update)
