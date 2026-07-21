# === ARP Faza 4C - refactored code ===
# sample_id: requests_007
# condition: G
# timestamp: 2026-06-04T13:27:29
# original_cc: 17, original_mi: None
# changed_pct: 0.8831
# === END HEADER ===
def _prepare_json_body(self, json):
    """Prepares the body for a JSON request."""
    content_type = "application/json"
    try:
        body = complexjson.dumps(json, allow_nan=False)
    except ValueError as ve:
        raise InvalidJSONError(ve, request=self)

    if not isinstance(body, bytes):
        body = body.encode("utf-8")
    return body, content_type

def _is_stream_data(self, data):
    """Checks if the given data is a stream-like object."""
    return all(
        [
            hasattr(data, "__iter__"),
            not isinstance(data, (basestring, list, tuple, Mapping)),
        ]
    )

def _set_body_position_if_possible(self, body):
    """Records the current position of a readable file-like body."""
    if getattr(body, "tell", None) is not None:
        try:
            self._body_position = body.tell()
        except OSError:
            # This differentiates from None, allowing us to catch
            # a failed `tell()` later when trying to rewind the body