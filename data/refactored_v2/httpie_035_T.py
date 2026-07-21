# === ARP Faza 4C - refactored code ===
# sample_id: httpie_035
# condition: T
# timestamp: 2026-06-04T14:08:37
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def get_lexer_for_body(
    self, mime: str,
    body: str
) -> Optional[Type[Lexer]]:
    return get_lexer(
        mime=mime,
        explicit_json=self.explicit_json,
        body=body,
    )
