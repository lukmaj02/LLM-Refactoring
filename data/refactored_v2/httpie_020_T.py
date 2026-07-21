# === ARP Faza 4C - refactored code ===
# sample_id: httpie_020
# condition: T
# timestamp: 2026-06-04T14:05:55
# original_cc: 5, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __init__(
    self,
    env=Environment(),
    mime_overwrite: str = None,
    encoding_overwrite: str = None,
    **kwargs
):
    super().__init__(**kwargs)
    if mime_overwrite:
        self.mime = mime_overwrite
    else:
        self.mime, _ = parse_content_type_header(self.msg.content_type)
    self._encoding = encoding_overwrite or self.msg.encoding
    self._encoding_guesses = []
    if env.stdout_isatty:
        # Use the encoding supported by the terminal.
        output_encoding = env.stdout_encoding
    else:
        # Preserve the message encoding.
        output_encoding = self.msg.encoding
    # Default to UTF-8 when unsure.
    self.output_encoding = output_encoding or UTF8
