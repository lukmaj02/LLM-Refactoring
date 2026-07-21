# === ARP Faza 4C - refactored code ===
# sample_id: httpie_022
# condition: C
# timestamp: 2026-06-04T14:06:37
# original_cc: 5, original_mi: None
# changed_pct: 0.5806
# === END HEADER ===
def _resolve_style(style_name):
    try:
        PieStyle(style_name)
    except ValueError:
        return Styles.ANSI
    return Styles.PIE


def _extract_color_properties(color_set):
    if isinstance(color_set, _StyledGenericColor):
        return color_set.color, dict.fromkeys(color_set.styles, True)
    return color_set, {}


def _make_rich_color_theme(style_name: Optional[str] = None) -> 'Theme':
    from rich.style import Style
    from rich.theme import Theme

    style = _resolve_style(style_name)
    theme = Theme()

    for color, color_set in ChainMap(GenericColor.__members__, CUSTOM_STYLES).items():
        color_set, properties = _extract_color_properties(color_set)
        theme.styles[color.lower()] = Style(
            color=color_set.apply_style(style, style_name=style_name),
            **properties,
        )

    # E.g translate GenericColor.BLUE into blue on key access
    theme.styles = _GenericColorCaster(theme.styles)
    return theme