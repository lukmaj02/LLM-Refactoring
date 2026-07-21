# === ARP Faza 4C - refactored code ===
# sample_id: requests_007
# condition: A
# timestamp: 2026-06-04T13:24:58
# original_cc: 17, original_mi: None
# changed_pct: 0.7407
# === END HEADER ===
def prepare_body(self, data, files, json=None):
    """Prepares the given HTTP body data."""
    body, content_type = None, None

    if not data and json is not None:
        body, content_type = self._prepare_json_body(json)
    elif self._is_stream(data):
        body = self._prepare_stream_body(data, files)
    else:
        body, content_type = self._prepare_standard_body(data, files)

    self.body = body
    if content_type and ("content-type" not in self.headers):
        self.headers["Content-Type"] = content_type


def _prepare_json_body(self, json):
    """Prepare JSON body."""
    content_type = "application/json"
    try:
        body = complexjson.dumps(json, allow_nan=False)
    except ValueError as ve:
        raise InvalidJSONError(ve, request=self)

    if not isinstance(body, bytes):
        body = body.encode("utf-8")

    return body, content_type


def _is_stream(self, data):
    """Check if data is a stream."""
    return all(
        [
            hasattr(data, "__iter__"),
            not isinstance(data, (basestring, list, tuple, Mapping)),
        ]
    )


def _prepare_stream_body(self, data, files):
    """Prepare stream body."""
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

    return body


def _prepare_standard_body(self, data, files):
    """Prepare standard body."""
    body, content_type = None, None

    if files:
        body, content_type = self._encode_files(files, data)
    elif data:
        body = self._encode_params(data)
        if not isinstance(data, basestring) and not hasattr(data, "read"):
            content_type = "application/x-www-form-urlencoded"

    self.prepare_content_length(body)
    return body, content_type