# === ARP Faza 4C - refactored code ===
# sample_id: requests_034
# condition: A
# timestamp: 2026-06-04T13:55:52
# original_cc: 6, original_mi: None
# changed_pct: 0.7857
# === END HEADER ===
def raise_for_status(self):
    """Raises :class:`HTTPError`, if one occurred."""

    reason = self._decode_reason()
    http_error_msg = self._get_http_error_msg(reason)

    if http_error_msg:
        raise HTTPError(http_error_msg, response=self)

def _decode_reason(self):
    if isinstance(self.reason, bytes):
        try:
            return self.reason.decode("utf-8")
        except UnicodeDecodeError:
            return self.reason.decode("iso-8859-1")
    return self.reason

def _get_http_error_msg(self, reason):
    if 400 <= self.status_code < 500:
        return f"{self.status_code} Client Error: {reason} for url: {self.url}"
    elif 500 <= self.status_code < 600:
        return f"{self.status_code} Server Error: {reason} for url: {self.url}"
    return ""