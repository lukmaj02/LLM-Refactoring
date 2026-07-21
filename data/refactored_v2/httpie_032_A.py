# === ARP Faza 4C - refactored code ===
# sample_id: httpie_032
# condition: A
# timestamp: 2026-06-04T14:09:31
# original_cc: 2, original_mi: None
# changed_pct: 0.5200
# === END HEADER ===
def get_formatters(self, color_scheme: str) -> Tuple[
    pygments.formatter.Formatter,
    pygments.formatter.Formatter,
    bool
]:
    header_style, body_style, precise = self._get_styles_and_precision(color_scheme)
    return (
        Terminal256Formatter(style=header_style),
        Terminal256Formatter(style=body_style),
        precise
    )

def _get_styles_and_precision(self, color_scheme: str) -> Tuple[
    pygments.style.Style,
    pygments.style.Style,
    bool
]:
    if color_scheme in PIE_STYLES:
        header_style, body_style = PIE_STYLES[color_scheme]
        precise = True
    else:
        header_style = self.get_style_class(color_scheme)
        body_style = header_style
        precise = False
    return header_style, body_style, precise