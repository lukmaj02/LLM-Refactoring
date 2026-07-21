# === ARP Faza 4C - refactored code ===
# sample_id: httpie_027
# condition: C
# timestamp: 2026-06-04T14:08:08
# original_cc: 5, original_mi: None
# changed_pct: 0.4762
# === END HEADER ===
def format_body(self, body: str, mime: str):
    if 'xml' not in mime:
        return body

    from xml.parsers.expat import ExpatError
    from defusedxml.common import DefusedXmlException

    declaration = parse_declaration(body)
    try:
        parsed_body = parse_xml(body)
    except (ExpatError, DefusedXmlException):
        return body  # Invalid or unsafe XML, ignore.

    return pretty_xml(parsed_body,
                      encoding=parsed_body.encoding,
                      indent=self.format_options['xml']['indent'],
                      declaration=declaration)