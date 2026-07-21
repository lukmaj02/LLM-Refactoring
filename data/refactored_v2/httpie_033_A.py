# === ARP Faza 4C - refactored code ===
# sample_id: httpie_033
# condition: A
# timestamp: 2026-06-04T14:09:41
# original_cc: 2, original_mi: None
# changed_pct: 0.2000
# === END HEADER ===
def smart_decode(content: ContentBytes, encoding: str) -> Tuple[str, str]:
    """Decode `content` using the given `encoding`.
    If no `encoding` is provided, the best effort is to guess it from `content`.

    Unicode errors are replaced.

    """
    encoding = encoding or detect_encoding(content)
    return content.decode(encoding, 'replace'), encoding