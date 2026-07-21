# === ARP Faza 4C - refactored code ===
# sample_id: flask_015
# condition: A
# timestamp: 2026-06-04T14:14:31
# original_cc: 8, original_mi: None
# changed_pct: 0.4615
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

    def _execute_preprocessors(preprocessors, *args):
        for name in names:
            if name in preprocessors:
                for func in preprocessors[name]:
                    result = func(*args)
                    if result is not None:
                        return result
        return None

    _execute_preprocessors(self.url_value_preprocessors, request.endpoint, request.view_args)

    return _execute_preprocessors(self.before_request_funcs)