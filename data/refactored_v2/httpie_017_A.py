# === ARP Faza 4C - refactored code ===
# sample_id: httpie_017
# condition: A
# timestamp: 2026-06-04T14:05:12
# original_cc: 12, original_mi: None
# changed_pct: 0.7368
# === END HEADER ===
def to_usage(
    spec: ParserSpec,
    *,
    program_name: Optional[str] = None,
    whitelist: AbstractSet[str] = frozenset()
) -> RenderableType:
    shown_arguments = _get_shown_arguments(spec, whitelist)
    text = Text(program_name or spec.program, style=STYLE_BOLD)
    
    for argument in shown_arguments:
        text.append(' ')
        name = _get_argument_name(argument, whitelist)
        nargs = argument.configuration.get('nargs')
        _append_argument_text(text, name, nargs, whitelist, argument)
        _append_choices_text(text, argument)

    return text


def _get_shown_arguments(spec, whitelist):
    shown_arguments = [
        argument
        for group in spec.groups
        for argument in group.arguments
        if (not argument.aliases or whitelist.intersection(argument.aliases))
    ]
    shown_arguments.sort(key=lambda argument: argument.aliases, reverse=True)
    return shown_arguments


def _get_argument_name(argument, whitelist):
    if argument.aliases:
        return '/'.join(sorted(argument.aliases, key=len))
    return argument.metavar


def _append_argument_text(text, name, nargs, whitelist, argument):
    is_whitelisted = whitelist.intersection(argument.aliases)
    if nargs is Qualifiers.OPTIONAL:
        text.append('[' + name + ']', style=STYLE_USAGE_OPTIONAL)
    elif nargs is Qualifiers.ZERO_OR_MORE:
        text.append('[' + name + ' ...]', style=STYLE_USAGE_OPTIONAL)
    else:
        text.append(
            name,
            style=STYLE_USAGE_ERROR if is_whitelisted else STYLE_USAGE_REGULAR,
        )


def _append_choices_text(text, argument):
    raw_form = argument.serialize()
    if raw_form.get('choices'):
        text.append(' ')
        text.append(
            '{' + ', '.join(raw_form['choices']) + '}',
            style=STYLE_USAGE_MISSING,
        )