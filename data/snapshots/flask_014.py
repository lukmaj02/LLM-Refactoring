# SNAPSHOT METADATA
# sample_id: flask_014
# repo: flask
# file: data/repos/flask/src/flask/json/provider.py
# function: JSONProvider._prepare_response_obj
# cc: 7 | mi: N/A | loc: 13
# extracted: 2026-05-01T11:47:37

def _prepare_response_obj(
    self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
) -> t.Any:
    if args and kwargs:
        raise TypeError("app.json.response() takes either args or kwargs, not both")

    if not args and not kwargs:
        return None

    if len(args) == 1:
        return args[0]

    return args or kwargs
