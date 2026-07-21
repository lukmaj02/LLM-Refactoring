# SNAPSHOT METADATA
# sample_id: httpie_034
# repo: httpie
# file: data/repos/httpie/httpie/cli/nested_json/tokens.py
# function: TokenKind.to_name
# cc: 4 | mi: N/A | loc: 6
# extracted: 2026-05-01T11:47:36

def to_name(self) -> str:
    for key, value in OPERATORS.items():
        if value is self:
            return repr(key)
    else:
        return 'a ' + self.name.lower()
