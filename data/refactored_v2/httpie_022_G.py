# === ARP Faza 4C - refactored code ===
# sample_id: httpie_022
# condition: G
# timestamp: 2026-06-04T14:06:48
# original_cc: 5, original_mi: None
# changed_pct: 0.6512
# === END HEADER ===
def _get_theme_style(style_name: Optional[str]) -> Styles:
    try:
        PieStyle(style_name)
    except ValueError:
        return Styles.ANSI
    else:
        return Styles.PIE


def _get_rich_style_components(color_value: Any) -> tuple[Any, dict]:
    """
    Extracts properties and the base color from a color_value.
    Returns (base_color, properties_dict).
    """
    if isinstance(color_value, _StyledGenericColor):
        properties = dict.fromkeys(color_value.styles, True)
        base_color = color_value.color
    else:
        properties = {}
        base_color = color_value
    return base_color, properties


def _make_rich_color_theme(style_name: Optional[str] = None) -> 'Theme':
    from rich.style import Style
    from rich.theme import Theme

    style = _get_theme_style(style_name)

    theme = Theme()
    for color_key, color_value in ChainMap(
        GenericColor.__members__, CUSTOM_STYLES
    ).items():
        base_color, properties = _get_rich_style_components(color_value)

        theme.styles[color_key.lower()] = Style(
            color=base_color.apply_style(style, style_name=style_name),
            **properties,
        )

    # E.g translate GenericColor.BLUE into blue on key access
    theme.styles = _GenericColorCaster(theme.styles)
    return theme