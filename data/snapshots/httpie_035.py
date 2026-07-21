# SNAPSHOT METADATA
# sample_id: httpie_035
# repo: httpie
# file: data/repos/httpie/httpie/output/formatters/colors.py
# function: ColorFormatter.get_lexer_for_body
# cc: 1 | mi: N/A | loc: 8
# extracted: 2026-05-01T11:47:36

def get_lexer_for_body(
    self, mime: str,
    body: str
) -> Optional[Type[Lexer]]:
    return get_lexer(
        mime=mime,
        explicit_json=self.explicit_json,
        body=body,
    )
