# === ARP Faza 4C - refactored code ===
# sample_id: requests_022
# condition: G
# timestamp: 2026-06-04T13:39:23
# original_cc: 8, original_mi: None
# changed_pct: 0.5588
# === END HEADER ===
def _json_loads_with_requests_error(data, **kwargs):
    """Helper to load JSON data and re-raise JSONDecodeError as RequestsJSONDecodeError."""
    try:
        return complexjson.loads(data, **kwargs)
    except JSONDecodeError as e:
        raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)


def json(self, **kwargs):
    r"""Returns the json-encoded content of a response, if any.

    :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
    :raises requests.exceptions.JSONDecodeError: If the response body does not
        contain valid json.
    """

    # If no encoding is explicitly set, and content is available and long enough
    # for detection, attempt to guess the JSON encoding.
    if not self.encoding and self.content and len(self.content) > 3:
        encoding = guess_json_utf(self.content)
        if encoding is not None:
            try:
                # Try decoding with the guessed encoding and then loading JSON.
                decoded_content = self.content.decode(encoding)
                return _json_loads_with_requests_error(decoded_content, **kwargs)
            except UnicodeDecodeError:
                # If decoding fails with the guessed UTF codec, it's likely
                # not a standard UTF encoding. Fall through to the self.text
                # approach, which uses charset_normalizer for a best guess.
                pass

    # Fallback: use self.text, which handles encoding detection internally
    # (via self.apparent_encoding if self.encoding is None).
    return _json_loads_with_requests_error(self.text, **kwargs)