# === ARP Faza 4C - refactored code ===
# sample_id: flask_021
# condition: A
# timestamp: 2026-06-04T14:15:59
# original_cc: 7, original_mi: None
# changed_pct: 0.6047
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
            exc = self._get_exception(exc)
            self.app.do_teardown_request(exc)
            self._close_request()
    finally:
        self._finalize_context(exc, clear_request)

def _get_exception(self, exc):
    if exc is _sentinel:
        return sys.exc_info()[1]
    return exc

def _close_request(self):
    request_close = getattr(self.request, "close", None)
    if request_close is not None:
        request_close()

def _finalize_context(self, exc, clear_request):
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