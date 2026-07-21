# === ARP Faza 4C - refactored code ===
# sample_id: flask_016
# condition: G
# timestamp: 2026-06-04T14:17:58
# original_cc: 6, original_mi: None
# changed_pct: 0.3235
# === END HEADER ===
def trap_http_exception(self, e: Exception) -> bool:
    """Checks if an HTTP exception should be trapped or not.  By default
    this will return ``False`` for all exceptions except for a bad request
    key error if ``TRAP_BAD_REQUEST_ERRORS`` is set to ``True``.  It
    also returns ``True`` if ``TRAP_HTTP_EXCEPTIONS`` is set to ``True``.

    This is called for all HTTP exceptions raised by a view function.
    If it returns ``True`` for any exception the error handler for this
    exception is not called and it shows up as regular exception in the
    traceback.  This is helpful for debugging implicitly raised HTTP
    exceptions.

    .. versionchanged:: 1.0
        Bad request errors are not trapped by default in debug mode.

    .. versionadded:: 0.8
    """
    if self.config["TRAP_HTTP_EXCEPTIONS"]:
        return True

    trap_bad_request = self.config["TRAP_BAD_REQUEST_ERRORS"]

    # If TRAP_BAD_REQUEST_ERRORS is unset (None), trap key errors in debug mode.
    if trap_bad_request is None:
        return self.debug and isinstance(e, BadRequestKeyError)

    # If TRAP_BAD_REQUEST_ERRORS is explicitly True or False,
    # trap BadRequest exceptions only if it's True.
    return trap_bad_request and isinstance(e, BadRequest)