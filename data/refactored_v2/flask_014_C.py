# === ARP Faza 4C - refactored code ===
# sample_id: flask_014
# condition: C
# timestamp: 2026-06-04T14:14:39
# original_cc: 7, original_mi: None
# changed_pct: 0.2500
# === END HEADER ===
def _prepare_response_obj(
    self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
) -> t.Any:
    if args and kwargs:
        raise TypeError("app.json.response() takes either args or kwargs, not both")

    if not args and not kwargs:
        return None

    if kwargs:
        return kwargs

    if len(args) == 1:
        return args[0]

    return args