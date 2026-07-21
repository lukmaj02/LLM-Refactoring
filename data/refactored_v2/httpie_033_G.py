# === ARP Faza 4C - refactored code ===
# sample_id: httpie_033
# condition: G
# timestamp: 2026-06-04T14:10:34
# original_cc: 2, original_mi: None
# changed_pct: 0.6500
# === END HEADER ===
def _get_effective_encoding(content: ContentBytes, encoding_hint: str) -> str:
    """
    Determines the effective encoding to use.
    If `encoding_hint` is empty, it guesses the encoding from `content`.
    Otherwise, it uses `encoding_hint`.
    """
    if not encoding_hint:
        return detect_encoding(content)
    return encoding_hint


def smart_decode(content: ContentBytes, encoding: str) -> Tuple[str, str]:
    """Decode `content` using the given `encoding`.
    If no `encoding` is provided, the best effort is to guess it from `content`.

    Unicode errors are replaced.

    """
    effective_encoding = _get_effective_encoding(content, encoding)
    return content.decode(effective_encoding, 'replace'), effective_encoding