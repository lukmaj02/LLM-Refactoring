# === ARP Faza 4C - refactored code ===
# sample_id: httpie_016
# condition: C
# timestamp: 2026-06-04T14:04:26
# original_cc: 15, original_mi: None
# changed_pct: 0.5846
# === END HEADER ===
def _build_mime_candidates(mime: str):
    mime_types, lexer_names = [mime], []
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


def _find_lexer_by_mime_types(mime_types):
    for mime_type in mime_types:
        try:
            return pygments.lexers.get_lexer_for_mimetype(mime_type)
        except ClassNotFound:
            pass
    return None


def _find_lexer_by_names(lexer_names):
    for name in lexer_names:
        try:
            return pygments.lexers.get_lexer_by_name(name)
        except ClassNotFound:
            pass
    return None


def _try_json_lexer_for_body(body: str):
    try:
        json.loads(body)  # FIXME: the body also gets parsed in json.py
    except ValueError:
        return None
    return pygments.lexers.get_lexer_by_name('json')


def get_lexer(
    mime: str,
    explicit_json=False,
    body=''
) -> Optional[Type[Lexer]]:
    mime_types, lexer_names = _build_mime_candidates(mime)

    lexer = _find_lexer_by_mime_types(mime_types)
    if lexer is None:
        lexer = _find_lexer_by_names(lexer_names)

    if explicit_json and body and (not lexer or isinstance(lexer, TextLexer)):
        # JSON response with an incorrect Content-Type?
        lexer = _try_json_lexer_for_body(body) or lexer

    if isinstance(lexer, JsonLexer):
        lexer = EnhancedJsonLexer()

    return lexer