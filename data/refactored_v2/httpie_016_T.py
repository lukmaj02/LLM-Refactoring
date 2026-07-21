# === ARP Faza 4C - refactored code ===
# sample_id: httpie_016
# condition: T
# timestamp: 2026-06-04T14:05:03
# original_cc: 15, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def get_lexer(
    mime: str,
    explicit_json=False,
    body=''
) -> Optional[Type[Lexer]]:
    # Build candidate mime type and lexer names.
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

    # As a last resort, if no lexer feels responsible, and
    # the subtype contains 'json', take the JSON lexer
    if 'json' in subtype:
        lexer_names.append('json')

    # Try to resolve the right lexer.
    lexer = None
    for mime_type in mime_types:
        try:
            lexer = pygments.lexers.get_lexer_for_mimetype(mime_type)
            break
        except ClassNotFound:
            pass
    else:
        for name in lexer_names:
            try:
                lexer = pygments.lexers.get_lexer_by_name(name)
            except ClassNotFound:
                pass

    if explicit_json and body and (not lexer or isinstance(lexer, TextLexer)):
        # JSON response with an incorrect Content-Type?
        try:
            json.loads(body)  # FIXME: the body also gets parsed in json.py
        except ValueError:
            pass  # Nope
        else:
            lexer = pygments.lexers.get_lexer_by_name('json')

    # Use our own JSON lexer: it supports JSON bodies preceded by non-JSON data
    # as well as legit JSON bodies.
    if isinstance(lexer, JsonLexer):
        lexer = EnhancedJsonLexer()

    return lexer
