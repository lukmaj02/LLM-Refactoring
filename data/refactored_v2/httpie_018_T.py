# === ARP Faza 4C - refactored code ===
# sample_id: httpie_018
# condition: T
# timestamp: 2026-06-04T14:05:35
# original_cc: 11, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def to_help_message(
    spec: ParserSpec,
) -> Iterable[RenderableType]:
    yield Padding(
        options_highlighter(spec.description),
        LEFT_INDENT_2,
    )

    yield Padding(
        Text('Usage', style=STYLE_SWITCH),
        LEFT_INDENT_2,
    )
    yield Padding(to_usage(spec), LEFT_INDENT_3)

    group_rows = {}
    for group in spec.groups:
        options_rows = []

        for argument in group.arguments:
            if argument.is_hidden:
                continue

            opt1, opt2 = unpack_argument(argument)
            if opt2:
                opt1.append('/')
                opt1.append(opt2)

            # Column for a metavar, if we have one
            metavar = Text(style=STYLE_METAVAR)
            metavar.append(argument.configuration.get('metavar', ''))

            if opt1 == metavar:
                metavar = Text('')

            raw_form = argument.serialize()
            desc = raw_form.get('short_description', '')
            if raw_form.get('choices'):
                desc += ' (choices: '
                desc += textwrap.shorten(
                    ', '.join(raw_form.get('choices')),
                    MAX_CHOICE_CHARS,
                )
                desc += ')'

            rows = [
                Padding(
                    options_highlighter(opt1),
                    LEFT_PADDING_2,
                ),
                metavar,
                options_highlighter(desc),
            ]

            options_rows.append(rows)
            if argument.configuration.get('nested_options'):
                options_rows.extend(
                    [
                        (
                            Padding(
                                Text(
                                    key,
                                    style=STYLE_USAGE_OPTIONAL,
                                ),
                                LEFT_PADDING_4,
                            ),
                            value,
                            dec,
                        )
                        for key, value, dec in argument.nested_options
                    ]
                )

        group_rows[group.name] = options_rows

    options_table = Table(highlight=False, box=None, show_header=False)
    for group_name, options_rows in group_rows.items():
        options_table.add_row(Text(), Text(), Text())
        options_table.add_row(
            Text(group_name, style=STYLE_SWITCH),
            Text(),
            Text(),
        )
        options_table.add_row(Text(), Text(), Text())
        for row in options_rows:
            options_table.add_row(*row)

    yield Padding(
        Text('Options', style=STYLE_SWITCH),
        LEFT_INDENT_2,
    )
    yield Padding(options_table, LEFT_PADDING_2)
    yield Padding(
        Text('More Information', style=STYLE_SWITCH),
        LEFT_INDENT_2,
    )
    yield Padding(
        MORE_INFO_COMMANDS.rstrip('\n'),
        LEFT_PADDING_3
    )
    yield Padding(
        spec.epilog.rstrip('\n'),
        LEFT_INDENT_BOTTOM_3,
    )
