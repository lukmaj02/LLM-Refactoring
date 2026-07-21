# SNAPSHOT METADATA
# sample_id: httpie_027
# repo: httpie
# file: data/repos/httpie/httpie/output/formatters/xml.py
# function: XMLFormatter.format_body
# cc: 5 | mi: N/A | loc: 21
# extracted: 2026-05-01T11:47:36

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
