# === ARP Faza 4C - refactored code ===
# sample_id: requests_007
# condition: C
# timestamp: 2026-06-04T13:24:57
# original_cc: 17, original_mi: None
# changed_pct: 0.7356
# === END HEADER ===
def _prepare_json_body(self, json):
    """Encode a JSON body, returning (body_bytes, content_type)."""
    content_type = "application/json"
    try:
        body = complexjson.dumps(json, allow_nan=False)
    except ValueError as ve:
        raise InvalidJSONError(ve, request=self)
    if not isinstance(body, bytes):
        body = body.encode("utf-8")
    return body, content_type


def _prepare_stream_body(self, data, files):
    """Handle a streaming body, setting appropriate headers."""
    try:
        length = super_len(data)
    except (TypeError, AttributeError, UnsupportedOperation):
        length = None

    body = data

    if getattr(body, "tell", None) is not None:
        try:
            self._body_position = body.tell()
        except OSError:
            self._body_position = object()

    if files:
        raise NotImplementedError(
            "Streamed bodies and files are mutually exclusive."
        )

    if length:
        self.headers["Content-Length"] = builtin_str(length)
    else:
        self.headers["Transfer-Encoding"] = "chunked"

    return body, None


def _prepare_encoded_body(self, data, files):
    """Handle a non-streaming body with optional files, returning (body, content_type)."""
    if files:
        return self._encode_files(files, data)

    if not data:
        return None, None

    body = self._encode_params(data)
    if isinstance(data, basestring) or hasattr(data, "read"):
        content_type = None
    else:
        content_type = "application/x-www-form-urlencoded"
    return body, content_type


def prepare_body(self, data, files, json=None):
    """Prepares the given HTTP body data."""

    body = None
    content_type = None

    if not data and json is not None:
        body, content_type = self._prepare_json_body(json)

    is_stream = all(
        [
            hasattr(data, "__iter__"),
            not isinstance(data, (basestring, list, tuple, Mapping)),
        ]
    )

    if is_stream:
        body, content_type = self._prepare_stream_body(data, files)
    else:
        encoded_body, encoded_content_type = self._prepare_encoded_body(data, files)
        if encoded_body is not None:
            body = encoded_body
        if encoded_content_type is not None:
            content_type = encoded_content_type

        self.prepare_content_length(body)

        if content_type and "content-type" not in self.headers:
            self.headers["Content-Type"] = content_type

    self.body = body