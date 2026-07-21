# === ARP Faza 4C - refactored code ===
# sample_id: httpie_027
# condition: G
# timestamp: 2026-06-04T14:08:18
# original_cc: 5, original_mi: None
# changed_pct: 0.9667
# === END HEADER ===
def _try_format_xml_body(self, body: str) -> Optional[str]:
        """
        Attempts to parse and prettify an XML body.
        Returns the prettified XML string if successful, otherwise None.
        """
        from xml.parsers.expat import ExpatError
        from defusedxml.common import DefusedXmlException

        declaration = parse_declaration(body)
        try:
            parsed_body = parse_xml(body)
        except (ExpatError, DefusedXmlException):
            # Invalid or unsafe XML, return None to indicate failure.
            return None
        else:
            return pretty_xml(
                parsed_body,
                encoding=parsed_body.encoding,
                indent=self.format_options['xml']['indent'],
                declaration=declaration
            )

    def format_body(self, body: str, mime: str):
        if 'xml' not in mime:
            return body

        formatted_body = self._try_format_xml_body(body)
        if formatted_body is not None:
            return formatted_body
        return body