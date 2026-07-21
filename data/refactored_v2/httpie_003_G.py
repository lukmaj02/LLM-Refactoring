# === ARP Faza 4C - refactored code ===
# sample_id: httpie_003
# condition: G
# timestamp: 2026-06-04T13:57:47
# original_cc: 27, original_mi: None
# changed_pct: 0.9911
# === END HEADER ===
def _handle_generic_error(e: Exception, env: Environment, include_traceback: bool, annotation: Optional[str] = None):
    """
    Logs a generic error and optionally re-raises it based on include_traceback.
    """
    msg = str(e)
    if hasattr(e, 'request'):
        request = e.request
        if hasattr(request, 'url'):
            msg = (
                f'{msg} while doing a {request.method}'
                f' request to URL: {request.url}'
            )
    if annotation:
        msg += annotation
    env.log_error(f'{type(e).__name__}: {msg}')
    if include_