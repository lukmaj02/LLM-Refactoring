# === ARP Faza 4C - refactored code ===
# sample_id: httpie_016
# condition: A
# timestamp: 2026-06-04T14:04:40
# original_cc: 15, original_mi: None
# changed_pct: 0.5636
# === END HEADER ===
def get_lexer(
    mime: str,
    explicit_json=False,
    body=''
) -> Optional[Type[Lexer]]:
    mime_types, lexer_names = _build_mime_and_lexer_names(mime)

    lexer = _resolve_lexer(mime_types, lexer_names)

    if explicit_json and body and (not lexer or isinstance(lexer, TextLexer)):
        lexer = _attempt_json_lexer(body)

    if isinstance(lexer, JsonLexer):
        lexer = EnhancedJsonLexer()

    return lexer


def _build_mime_and_lexer_names(mime: str):
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


def _resolve_lexer(mime_types, lexer_names):
    for mime_type in mime_types:
        try:
            return pygments.lexers.get_lexer_for_mimetype(mime_type)
        except ClassNotFound:
            continue
    for name in lexer_names:
        try:
            return pygments.lexers.get_lexer_by_name(name)
        except ClassNotFound:
            continue
    return None


def _attempt_json_lexer(body: str):
    try:
        json.loads(body)
        return pygments.lexers.get_lexer_by_name('json')
    except ValueError:
        return None