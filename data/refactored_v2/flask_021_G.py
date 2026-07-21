# === ARP Faza 4C - refactored code ===
# sample_id: flask_021
# condition: G
# timestamp: 2026-06-04T14:19:40
# original_cc: 7, original_mi: None
# changed_pct: 0.3947
# === END HEADER ===
def _perform_request_teardown(self, exc: BaseException | None) -> None:
    self.app.do_teardown_request(exc)

    request_close = getattr(self.request, "close", None)
    if request_close is not None:
        request_close()


def pop(self, exc: BaseException | None = _sentinel) -> None:  # type: ignore
    """Pops the request context and unbinds it by doing that.  This will
    also trigger the execution of functions registered by the
    :meth:`~flask.Flask.teardown_request` decorator.

    .. versionchanged:: 0.9
       Added the `exc` argument.
    """
    if exc is _sentinel:
        current_exc = sys.exc_info()[1]
    else:
        current_exc = exc

    clear_request = len(self._cv_tokens) == 1

    try:
        if clear_request:
            self._perform_request_teardown(current_exc)
    finally:
        ctx = _cv_request.get()
        token, app_ctx = self._cv_tokens.pop()
        _cv_request.reset(token)

        # get rid of circular dependencies at the end of the request
        # so that we don't require the GC to be active.
        if clear_request:
            ctx.request.environ["werkzeug.request"] = None

        if app_ctx is not None:
            app_ctx