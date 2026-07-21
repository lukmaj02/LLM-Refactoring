# === ARP Faza 4C - refactored code ===
# sample_id: flask_015
# condition: G
# timestamp: 2026-06-04T14:17:40
# original_cc: 8, original_mi: None
# changed_pct: 0.5714
# === END HEADER ===
def _run_url_value_preprocessors(self, names: t.Iterable[str | None]) -> None:
    for name in names:
        if name in self.url_value_preprocessors:
            for url_func in self.url_value_preprocessors[name]:
                url_func(request.endpoint, request.view_args)

def _run_before_request_funcs(self, names: t.Iterable[str | None]) -> ft.ResponseReturnValue | None:
    for name in names:
        if name in self.before_request_funcs:
            for before_func in self.before_request_funcs[name]:
                rv = self.ensure_sync(before_func)()

                if rv is not None:
                    return rv
    return None

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

    self._run_url_value_preprocessors(names)

    rv = self._run_before_request_funcs(names)
    if rv is not None:
        return rv

    return None