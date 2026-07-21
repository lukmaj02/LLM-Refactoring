# SNAPSHOT METADATA
# sample_id: httpie_017
# repo: httpie
# file: data/repos/httpie/httpie/output/ui/rich_help.py
# function: to_usage
# cc: 12 | mi: N/A | loc: 52
# extracted: 2026-05-01T11:47:36

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
