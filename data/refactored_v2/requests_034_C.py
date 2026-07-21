# === ARP Faza 4C - refactored code ===
# sample_id: requests_034
# condition: C
# timestamp: 2026-06-04T13:56:49
# original_cc: 6, original_mi: None
# changed_pct: 0.7500
# === END HEADER ===
def _decode_reason(reason):
    if isinstance(reason, bytes):
        try:
            return reason.decode("utf-8")
        except UnicodeDecodeError:
            return reason.decode("iso-8859-1")
    return reason


def _get_error_type(status_code):
    if 400 <= status_code < 500:
        return "Client"
    if 500 <= status_code < 600:
        return "Server"
    return None


def raise_for_status(self):
    """Raises :class:`HTTPError`, if one occurred."""

    reason = _decode_reason(self.reason)
    error_type = _get_error_type(self.status_code)

    if error_type is not None:
        http_error_msg = (
            f"{self.status_code} {error_type} Error: {reason} for url: {self.url}"
        )
        raise HTTPError(http_error_msg, response=self)