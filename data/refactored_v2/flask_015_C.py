# === ARP Faza 4C - refactored code ===
# sample_id: flask_015
# condition: C
# timestamp: 2026-06-04T14:15:04
# original_cc: 8, original_mi: None
# changed_pct: 0.3077
# === END HEADER ===
def preprocess_request(self) -> ft.ResponseReturnValue | None:
    """Called before the request is dispatched. Calls
    :attr:`url_value_preprocessors` registered with the app and the
    current blueprint (if any). Then calls :attr:`before_request_funcs`
    registered with the app and the blueprint.

    If any :meth:`before_request` handler returns a non-None value, the
    value is handled as if it was the return value from the view, and
    further request handling is stopped.
    """
    names = (None, *reversed(request.blueprints))

    for name in names:
        for url_func in self.url_value_preprocessors.get(name, ()):
            url_func(request.endpoint, request.view_args)

    for name in names:
        for before_func in self.before_request_funcs.get(name, ()):
            rv = self.ensure_sync(before_func)()

            if rv is not None:
                return rv  # type: ignore[no-any-return]

    return None