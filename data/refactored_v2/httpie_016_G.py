# === ARP Faza 4C - refactored code ===
# sample_id: httpie_016
# condition: G
# timestamp: 2026-06-04T14:03:50
# original_cc: 15, original_mi: None
# changed_pct: 0.6429
# === END HEADER ===
def _get_candidate_lexer_info(mime: str) -> Tuple[list, list]:
    """
    Builds candidate mime types and lexer names from the given mime string.
    """
    mime_types = [mime]
    lexer_names = []
    type_, subtype = mime.split('/', 1)

    if '+' not in subtype:
        lexer_names.append(subtype)
    else:
        subtype_name, subtype_suffix = subtype.split('+', 1)
        lexer_names.extend([subtype_name, subtype_suffix])
        mime_types.extend([
            f'{type_}/{subtype_name}',
            f'{type_}/{subtype_suffix}',
        ])

    if 'json' in subtype:
        lexer_names.append('json')

    return mime_types, lexer_names


def _resolve_lexer_from_candidates(
    mime_types: list,
    lexer_names: list
) -> Optional[Type[Lexer]]:
    """
    Attempts to resolve a Pygments lexer using a list of candidate mime types
    and then a list of candidate lexer names.
    """
    for mime_type in mime_types:
        try:
            return pygments.lexers.get_lexer_for_mimetype(mime_type)
        except ClassNotFound:
            pass

    for name in lexer_names:
        try:
            return pygments.lexers.get_lexer_by_name(name)
        except ClassNotFound:
            pass
    return None


def _try_json_fallback_if_generic_lexer(
    current_lexer: Optional[Type[Lexer]],
    body: str
) -> Optional[Type[Lexer]]:
    """
    If the current lexer is None or a generic TextLexer,
    try to parse the body as JSON and return a JsonLexer if successful.
    Returns None if no fallback is applied or if JSON parsing fails.
    """
    if not current_lexer or isinstance(current_lexer, TextLexer):
        try:
            json.loads(body)  # FIXME: the body also gets parsed in json.py
        except ValueError:
            return None  # Not JSON, no fallback
        else:
            return pygments.lexers.get_lexer_by_name('json')
    return None


def get_lexer(
    mime: str,
    explicit_json=False,
    body=''
) -> Optional[Type[Lexer]]:
    mime_types, lexer_names = _get_candidate_lexer_info(mime)
    lexer = _resolve_lexer_from_candidates(mime_types, lexer_names)

    if explicit_json and body:
        json_fallback_lexer = _try_json_fallback_if_generic_lexer(lexer, body)
        if json_fallback_lexer:
            lexer = json_fallback_lexer

    # Use our own JSON lexer: it supports JSON bodies preceded by non-JSON data
    # as well as legit JSON bodies.
    if isinstance(lexer, JsonLexer):
        lexer = EnhancedJsonLexer()

    return lexer