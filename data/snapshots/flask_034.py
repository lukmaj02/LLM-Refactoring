# SNAPSHOT METADATA
# sample_id: flask_034
# repo: flask
# file: data/repos/flask/src/flask/ctx.py
# function: RequestContext.__exit__
# cc: 1 | mi: N/A | loc: 7
# extracted: 2026-05-01T11:47:37

def __exit__(
    self,
    exc_type: type | None,
    exc_value: BaseException | None,
    tb: TracebackType | None,
) -> None:
    self.pop(exc_value)
