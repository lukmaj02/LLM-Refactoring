# === ARP Faza 4C - refactored code ===
# sample_id: flask_014
# condition: G
# timestamp: 2026-06-04T14:17:33
# original_cc: 7, original_mi: None
# changed_pct: 0.4118
# === END HEADER ===
def _prepare_response_obj(
    self, args: tuple[t.Any, ...], kwargs: dict[str, t.Any]
) -> t.Any:
    if args and kwargs:
        raise TypeError("app.json.response() takes either args or kwargs, not both")

    if not args and not kwargs:
        return None

    # At this point, exactly one of args or kwargs is non-empty.
    # If args is non-empty, kwargs must be empty.
    # If kwargs is non-empty, args must be empty.

    if args:
        # Only positional arguments are provided.
        if len(args) == 1:
            return args[0