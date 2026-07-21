# === ARP Faza 4C - refactored code ===
# sample_id: requests_034
# condition: G
# timestamp: 2026-06-04T13:54:24
# original_cc: 6, original_mi: None
# changed_pct: 0.8387
# === END HEADER ===
def _decode_reason(self, reason_bytes):
        """Decodes the reason string, handling potential localization and encoding issues."""
        if isinstance(reason_bytes, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                return reason_bytes.decode("utf-8")
            except UnicodeDecodeError:
                return reason_bytes.decode("iso-8859-1")
        return reason_bytes

    def raise_for_status(self):
        """Raises :class:`HTTPError`, if one occurred."""

        reason = self._decode_reason(self.reason)
        error_type = None

        if 400 <= self.status_code < 500:
            error_type = "Client Error"
        elif 500 <= self.status_code < 600:
            error_type = "Server Error"
        else:
            # No client or server error, so no HTTPError to raise.
            return

        http_error_msg = (
            f"{self.status_code} {error_type}: {reason} for url: {self.url}"
        )
        raise HTTPError(http_error_msg, response=self)