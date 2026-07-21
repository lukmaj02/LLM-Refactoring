# === ARP Faza 4C - refactored code ===
# sample_id: httpie_020
# condition: G
# timestamp: 2026-06-04T14:06:08
# original_cc: 5, original_mi: None
# changed_pct: 1.0000
# === END HEADER ===
def _determine_mime(self, mime_overwrite: Optional[str]) -> str:
        if mime_overwrite:
            return mime_overwrite
        else:
            return parse_content_type_header(self.msg.content_type)[0]

    def _determine_output_encoding(self, env: Environment) -> str:
        """Determine the output encoding based on environment and message."""
        if env.stdout_isatty:
            # Use the encoding supported by the terminal.
            output_encoding = env.stdout_encoding
        else:
            # Preserve the message encoding.
            output_encoding = self.msg.encoding
        # Default to UTF-8 when unsure.
        return output_encoding or UTF8

    def __init__(
        self,
        env=Environment(),
        mime_overwrite: str = None,
        encoding_overwrite: str = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.mime = self._determine_mime(mime_overwrite)