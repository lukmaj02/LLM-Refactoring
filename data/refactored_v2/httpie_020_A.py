# === ARP Faza 4C - refactored code ===
# sample_id: httpie_020
# condition: A
# timestamp: 2026-06-04T14:06:02
# original_cc: 5, original_mi: None
# changed_pct: 0.5000
# === END HEADER ===
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
    self.output_encoding = self._determine_output_encoding(env)

def _determine_output_encoding(self, env):
    if env.stdout_isatty:
        return env.stdout_encoding
    return self.msg.encoding or UTF8