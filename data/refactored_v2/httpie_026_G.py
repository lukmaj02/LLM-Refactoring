# === ARP Faza 4C - refactored code ===
# sample_id: httpie_026
# condition: G
# timestamp: 2026-06-04T14:08:05
# original_cc: 6, original_mi: None
# changed_pct: 0.6250
# === END HEADER ===
def _format_json_body_content(self, body: str) -> str:
        """
        Helper to load and format JSON content from the body.
        Returns the formatted JSON string with prefix, or the original body
        if parsing fails.
        """
        from ..utils import load_prefixed_json
        try:
            data_prefix, json_obj = load_prefixed_json(body)
        except ValueError:
            # Invalid JSON, ignore and return original body.
            return body
        else:
            # Indent, sort keys by name, and avoid
            # unicode escapes to improve readability.
            return data_prefix + json.dumps(
                obj=json_obj,
                sort_keys=self.format_options['json']['sort_keys'],
                ensure_ascii=False,
                indent=self.format_options['json']['indent']
            )

    def format_body(self, body: str, mime: str) -> str:
        maybe_json = [
            'json',
            'javascript',
            'text',
        ]
        if (self.kwargs['explicit_json']
                or any(token in mime for token in maybe_json)):
            body = self._format_json_body_content(body)
        return body