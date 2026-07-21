# === ARP Faza 4C - refactored code ===
# sample_id: httpie_026
# condition: T
# timestamp: 2026-06-04T14:06:56
# original_cc: 6, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def format_body(self, body: str, mime: str) -> str:
    maybe_json = [
        'json',
        'javascript',
        'text',
    ]
    if (self.kwargs['explicit_json']
            or any(token in mime for token in maybe_json)):
        from ..utils import load_prefixed_json
        try:
            data_prefix, json_obj = load_prefixed_json(body)
        except ValueError:
            pass  # Invalid JSON, ignore.
        else:
            # Indent, sort keys by name, and avoid
            # unicode escapes to improve readability.
            body = data_prefix + json.dumps(
                obj=json_obj,
                sort_keys=self.format_options['json']['sort_keys'],
                ensure_ascii=False,
                indent=self.format_options['json']['indent']
            )
    return body
