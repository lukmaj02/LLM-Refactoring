# === ARP Faza 4C - refactored code ===
# sample_id: httpie_027
# condition: A
# timestamp: 2026-06-04T14:08:14
# original_cc: 5, original_mi: None
# changed_pct: 0.5000
# === END HEADER ===
def format_body(self, body: str, mime: str):
    if 'xml' not in mime:
        return body

    declaration = parse_declaration(body)
    parsed_body = self._try_parse_xml(body)
    if parsed_body:
        body = pretty_xml(parsed_body,
                          encoding=parsed_body.encoding,
                          indent=self.format_options['xml']['indent'],
                          declaration=declaration)

    return body

def _try_parse_xml(self, body: str):
    from xml.parsers.expat import ExpatError
    from defusedxml.common import DefusedXmlException

    try:
        return parse_xml(body)
    except (ExpatError, DefusedXmlException):
        return None  # Invalid or unsafe XML, ignore.