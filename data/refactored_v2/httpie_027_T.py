# === ARP Faza 4C - refactored code ===
# sample_id: httpie_027
# condition: T
# timestamp: 2026-06-04T14:07:19
# original_cc: 5, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def format_body(self, body: str, mime: str):
    if 'xml' not in mime:
        return body

    from xml.parsers.expat import ExpatError
    from defusedxml.common import DefusedXmlException

    declaration = parse_declaration(body)
    try:
        parsed_body = parse_xml(body)
    except ExpatError:
        pass  # Invalid XML, ignore.
    except DefusedXmlException:
        pass  # Unsafe XML, ignore.
    else:
        body = pretty_xml(parsed_body,
                          encoding=parsed_body.encoding,
                          indent=self.format_options['xml']['indent'],
                          declaration=declaration)

    return body
