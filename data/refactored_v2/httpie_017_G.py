# === ARP Faza 4C - refactored code ===
# sample_id: httpie_017
# condition: G
# timestamp: 2026-06-04T14:04:29
# original_cc: 12, original_mi: None
# changed_pct: 0.6034
# === END HEADER ===
def _get_argument_display_name(argument: Argument) -> str:
    """Determines the display name for an argument based on its aliases or metavar."""
    if argument.aliases:
        return '/'.join(sorted(argument.aliases, key=len))
    return argument.metavar


def _append_argument_representation(
    text: Text, argument: Argument, is_whitelisted: bool
) -> None:
    """Appends the argument's name and choices to the Text object with appropriate styling."""
    name = _get_argument_display_name(argument)
    nargs = argument.configuration.get('nargs')

    if nargs is Qualifiers.OPTIONAL:
        text.append('[' + name + ']', style=STYLE_USAGE_OPTIONAL)
    elif nargs is Qualifiers.ZERO_OR_MORE:
        text.append(
            '[' + name + ' ...]',
            style=STYLE_USAGE_OPTIONAL,
        )
    else:
        style = STYLE_USAGE_ERROR if is_whitelisted else STYLE_USAGE_REGULAR
        text.append(name, style=style)

    raw_form = argument.serialize()
    if raw_form.get('choices'):
        text.append(' ')
        text.append(
            '{' + ', '.join(raw_form['choices']) + '}',
            style=STYLE_USAGE_MISSING,
        )


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
        _append_argument_representation(text, argument, is_whitelisted)

    return text