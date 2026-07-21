# === ARP Faza 4C - refactored code ===
# sample_id: httpie_022
# condition: T
# timestamp: 2026-06-04T14:06:14
# original_cc: 5, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def _make_rich_color_theme(style_name: Optional[str] = None) -> 'Theme':
    from rich.style import Style
    from rich.theme import Theme

    try:
        PieStyle(style_name)
    except ValueError:
        style = Styles.ANSI
    else:
        style = Styles.PIE

    theme = Theme()
    for color, color_set in ChainMap(
        GenericColor.__members__, CUSTOM_STYLES
    ).items():
        if isinstance(color_set, _StyledGenericColor):
            properties = dict.fromkeys(color_set.styles, True)
            color_set = color_set.color
        else:
            properties = {}

        theme.styles[color.lower()] = Style(
            color=color_set.apply_style(style, style_name=style_name),
            **properties,
        )

    # E.g translate GenericColor.BLUE into blue on key access
    theme.styles = _GenericColorCaster(theme.styles)
    return theme
