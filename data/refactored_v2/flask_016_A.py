# === ARP Faza 4C - refactored code ===
# sample_id: flask_016
# condition: A
# timestamp: 2026-06-04T14:14:44
# original_cc: 6, original_mi: None
# changed_pct: 0.7353
# === END HEADER ===
def trap_http_exception(self, e: Exception) -> bool:
    if self.config["TRAP_HTTP_EXCEPTIONS"]:
        return True

    trap_bad_request = self.config["TRAP_BAD_REQUEST_ERRORS"]

    if self._should_trap_bad_request_key_error(trap_bad_request, e):
        return True

    return trap_bad_request and isinstance(e, BadRequest)

def _should_trap_bad_request_key_error(self, trap_bad_request, e: Exception) -> bool:
    return (
        trap_bad_request is None
        and self.debug
        and isinstance(e, BadRequestKeyError)
    )