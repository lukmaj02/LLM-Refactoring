# === ARP Faza 4C - refactored code ===
# sample_id: httpie_022
# condition: A
# timestamp: 2026-06-04T14:06:45
# original_cc: 5, original_mi: None
# changed_pct: 0.4483
# === END HEADER ===
def _make_rich_color_theme(style_name: Optional[str] = None) -> 'Theme':
    from rich.style import Style
    from rich.theme import Theme

    def determine_style():
        try:
            PieStyle(style_name)
        except ValueError:
            return Styles.ANSI
        return Styles.PIE

    def get_properties_and_color(color_set):
        if isinstance(color_set, _StyledGenericColor):
            return dict.fromkeys(color_set.styles, True), color_set.color
        return {}, color_set

    style = determine_style()
    theme = Theme()
    for color, color_set in ChainMap(
        GenericColor.__members__, CUSTOM_STYLES
    ).items():
        properties, color_set = get_properties_and_color(color_set)
        theme.styles[color.lower()] = Style(
            color=color_set.apply_style(style, style_name=style_name),
            **properties,
        )

    theme.styles = _GenericColorCaster(theme.styles)
    return theme