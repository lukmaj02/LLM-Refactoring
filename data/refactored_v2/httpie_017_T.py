# === ARP Faza 4C - refactored code ===
# sample_id: httpie_017
# condition: T
# timestamp: 2026-06-04T14:05:23
# original_cc: 12, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def to_usage(
    spec: ParserSpec,
    *,
    program_name: Optional[str] = None,
    whitelist: AbstractSet[str] = frozenset()
) -> RenderableType:
    shown_arguments = [
        argument
        for group in spec.groups
        for argument in group.arguments
        if (not argument.aliases or whitelist.intersection(argument.aliases))
    ]

    # Sort the shown_arguments so that --dash options are
    # shown first
    shown_arguments.sort(key=lambda argument: argument.aliases, reverse=True)

    text = Text(program_name or spec.program, style=STYLE_BOLD)
    for argument in shown_arguments:
        text.append(' ')

        is_whitelisted = whitelist.intersection(argument.aliases)
        if argument.aliases:
            name = '/'.join(sorted(argument.aliases, key=len))
        else:
            name = argument.metavar

        nargs = argument.configuration.get('nargs')
        if nargs is Qualifiers.OPTIONAL:
            text.append('[' + name + ']', style=STYLE_USAGE_OPTIONAL)
        elif nargs is Qualifiers.ZERO_OR_MORE:
            text.append(
                '[' + name + ' ...]',
                style=STYLE_USAGE_OPTIONAL,
            )
        else:
            text.append(
                name,
                style=STYLE_USAGE_ERROR
                if is_whitelisted
                else STYLE_USAGE_REGULAR,
            )

        raw_form = argument.serialize()
        if raw_form.get('choices'):
            text.append(' ')
            text.append(
                '{' + ', '.join(raw_form['choices']) + '}',
                style=STYLE_USAGE_MISSING,
            )

    return text
