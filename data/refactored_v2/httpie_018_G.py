# === ARP Faza 4C - refactored code ===
# sample_id: httpie_018
# condition: G
# timestamp: 2026-06-04T14:05:05
# original_cc: 11, original_mi: None
# changed_pct: 0.9806
# === END HEADER ===
def _get_argument_display_name(argument: Argument) -> Text:
    """Constructs the display name for an argument, combining opt1 and opt2."""
    opt1, opt2 = unpack_argument(argument)
    if opt2:
        opt1.append('/')
        opt1.append(opt2)
    return opt1


def _get_argument_metavar_text(argument: Argument, display_name: Text) -> Text:
    """Constructs the metavar text for an argument."""
    metavar = Text(style=STYLE_METAVAR)
    metavar.append(argument.configuration.get('metavar', ''))
    # This comparison is likely always false due to style differences,