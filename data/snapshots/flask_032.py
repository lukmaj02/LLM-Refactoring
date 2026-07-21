# SNAPSHOT METADATA
# sample_id: flask_032
# repo: flask
# file: data/repos/flask/src/flask/ctx.py
# function: RequestContext.match_request
# cc: 2 | mi: N/A | loc: 9
# extracted: 2026-05-01T11:47:37

def match_request(self) -> None:
    """Can be overridden by a subclass to hook into the matching
    of the request.
    """
    try:
        result = self.url_adapter.match(return_rule=True)  # type: ignore
        self.request.url_rule, self.request.view_args = result  # type: ignore
    except HTTPException as e:
        self.request.routing_exception = e
