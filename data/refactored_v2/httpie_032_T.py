# === ARP Faza 4C - refactored code ===
# sample_id: httpie_032
# condition: T
# timestamp: 2026-06-04T14:08:17
# original_cc: 2, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
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
