# SNAPSHOT METADATA
# sample_id: httpie_032
# repo: httpie
# file: data/repos/httpie/httpie/output/formatters/colors.py
# function: ColorFormatter.get_formatters
# cc: 2 | mi: N/A | loc: 17
# extracted: 2026-05-01T11:47:36

def get_formatters(self, color_scheme: str) -> Tuple[
    pygments.formatter.Formatter,
    pygments.formatter.Formatter,
    bool
]:
    if color_scheme in PIE_STYLES:
        header_style, body_style = PIE_STYLES[color_scheme]
        precise = True
    else:
        header_style = self.get_style_class(color_scheme)
        body_style = header_style
        precise = False

    return (
        Terminal256Formatter(style=header_style),
        Terminal256Formatter(style=body_style),
        precise
    )
