# SNAPSHOT METADATA
# sample_id: httpie_033
# repo: httpie
# file: data/repos/httpie/httpie/encoding.py
# function: smart_decode
# cc: 2 | mi: N/A | loc: 10
# extracted: 2026-05-01T11:47:36

def smart_decode(content: ContentBytes, encoding: str) -> Tuple[str, str]:
    """Decode `content` using the given `encoding`.
    If no `encoding` is provided, the best effort is to guess it from `content`.

    Unicode errors are replaced.

    """
    if not encoding:
        encoding = detect_encoding(content)
    return content.decode(encoding, 'replace'), encoding
