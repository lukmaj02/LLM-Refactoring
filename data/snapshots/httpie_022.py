# SNAPSHOT METADATA
# sample_id: httpie_022
# repo: httpie
# file: data/repos/httpie/httpie/output/ui/rich_palette.py
# function: _make_rich_color_theme
# cc: 5 | mi: N/A | loc: 29
# extracted: 2026-05-01T11:47:36

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
