# === ARP Faza 4C - refactored code ===
# sample_id: httpie_014
# condition: G
# timestamp: 2026-06-04T14:02:46
# original_cc: 11, original_mi: None
# changed_pct: 0.9733
# === END HEADER ===
def _make_type_error_token(path: Path) -> Union[Token, None]:
    if path.tokens:
        return Token(
            kind=TokenKind.PSEUDO,
            value='',
            start=path.tokens[0].start,
            end=path.tokens[-1].end,
        )
    return None


def _raise_type_error(
    current_cursor: Any,
    index: int,
    path: Path,
    expected_type: JSONType,
    source_key: str,
    all_paths: list[Path]
):
    if not isinstance(current_cursor, expected_type):
        cursor_type = JSON_TYPE_