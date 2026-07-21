# === ARP Faza 4C - refactored code ===
# sample_id: httpie_020
# condition: C
# timestamp: 2026-06-04T14:06:03
# original_cc: 5, original_mi: None
# changed_pct: 0.5455
# === END HEADER ===
def _resolve_output_encoding(env, msg_encoding):
    if env.stdout_isatty:
        return env.stdout_encoding
    return msg_encoding


def __init__(
    self,
    env=Environment(),
    mime_overwrite: str = None,
    encoding_overwrite: str = None,
    **kwargs
):
    super().__init__(**kwargs)
    self.mime = mime_overwrite or parse_content_type_header(self.msg.content_type)[0]
    self._encoding = encoding_overwrite or self.msg.encoding
    self._encoding_guesses = []
    self.output_encoding = _resolve_output_encoding(env, self.msg.encoding) or UTF8