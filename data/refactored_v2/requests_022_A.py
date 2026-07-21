# === ARP Faza 4C - refactored code ===
# sample_id: requests_022
# condition: A
# timestamp: 2026-06-04T13:41:10
# original_cc: 8, original_mi: None
# changed_pct: 0.5000
# === END HEADER ===
def json(self, **kwargs):
    r"""Returns the json-encoded content of a response, if any.

    :param \*\*kwargs: Optional arguments that ``json.loads`` takes.
    :raises requests.exceptions.JSONDecodeError: If the response body does not
        contain valid json.
    """

    def decode_content_with_encoding(encoding):
        try:
            return complexjson.loads(self.content.decode(encoding), **kwargs)
        except UnicodeDecodeError:
            pass
        except JSONDecodeError as e:
            raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)

    if not self.encoding and self.content and len(self.content) > 3:
        encoding = guess_json_utf(self.content)
        if encoding is not None:
            result = decode_content_with_encoding(encoding)
            if result is not None:
                return result

    try:
        return complexjson.loads(self.text, **kwargs)
    except JSONDecodeError as e:
        raise RequestsJSONDecodeError(e.msg, e.doc, e.pos)