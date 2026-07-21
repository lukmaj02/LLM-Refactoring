# === ARP Faza 4C - refactored code ===
# sample_id: flask_021
# condition: C
# timestamp: 2026-06-04T14:16:35
# original_cc: 7, original_mi: None
# changed_pct: 0.2895
# === END HEADER ===
def pop(self, exc: BaseException | None = _sentinel) -> None:  # type: ignore
    """Pops the request context and unbinds it by doing that.  This will
    also trigger the execution of functions registered by the
    :meth:`~flask.Flask.teardown_request` decorator.

    .. versionchanged:: 0.9
       Added the `exc` argument.
    """
    clear_request = len(self._cv_tokens) == 1

    try:
        if clear_request:
            self._teardown_request(exc)
    finally:
        ctx = _cv_request.get()
        token, app_ctx = self._cv_tokens.pop()
        _cv_request.reset(token)

        if clear_request:
            ctx.request.environ["werkzeug.request"] = None

        if app_ctx is not None:
            app_ctx.pop(exc)

        if ctx is not self:
            raise AssertionError(
                f"Popped wrong request context. ({ctx!r} instead of {self!r})"
            )

def _teardown_request(self, exc: BaseException | None) -> None:
    if exc is _sentinel:
        exc = sys.exc_info()[1]

    self.app.do_teardown_request(exc)

    request_close = getattr(self.request, "close", None)
    if request_close is not None:
        request_close()