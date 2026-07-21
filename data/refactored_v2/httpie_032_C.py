# === ARP Faza 4C - refactored code ===
# sample_id: httpie_032
# condition: C
# timestamp: 2026-06-04T14:09:14
# original_cc: 2, original_mi: None
# changed_pct: 0.1111
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
        header_style = body_style = self.get_style_class(color_scheme)
        precise = False

    return (
        Terminal256Formatter(style=header_style),
        Terminal256Formatter(style=body_style),
        precise
    )