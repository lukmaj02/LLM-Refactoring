# === ARP Faza 4C - refactored code ===
# sample_id: requests_009
# condition: G
# timestamp: 2026-06-04T13:28:19
# original_cc: 15, original_mi: None
# changed_pct: 0.9590
# === END HEADER ===
def _update_history_and_check_limit(self, resp, hist):
    """Updates history, consumes response content, checks redirect limit, and closes the response."""
    hist.append(resp)
    resp.history = hist[1:]

    try:
        resp.content  # Consume socket so it can be released
    except (ChunkedEncodingError, ContentDecodingError, RuntimeError):
        resp.raw.read(decode_content=False)

    if len(resp.history) >= self.max_redirects:
        raise TooManyRedirects(
            f"Exceeded {self.max_redirects} redirects.", response=resp
        )

    resp.close()

def _normalize_redirect_