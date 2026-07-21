# === ARP Faza 4C - refactored code ===
# sample_id: requests_025
# condition: C
# timestamp: 2026-06-04T13:45:51
# original_cc: 6, original_mi: None
# changed_pct: 0.4054
# === END HEADER ===
def _parse_link_params(params, replace_chars):
    """Parse semicolon-separated key=value parameters into a dict."""
    result = {}
    for param in params.split(";"):
        try:
            key, value = param.split("=")
        except ValueError:
            break
        result[key.strip(replace_chars)] = value.strip(replace_chars)
    return result


def parse_header_links(value):
    """Return a list of parsed link headers proxies.

    i.e. Link: <http:/.../front.jpeg>; rel=front; type="image/jpeg",<http://.../back.jpeg>; rel=back;type="image/jpeg"

    :rtype: list
    """
    replace_chars = " '\""

    value = value.strip(replace_chars)
    if not value:
        return []

    links = []
    for val in re.split(", *<", value):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ""

        link = {"url": url.strip("<> '\"")}
        link.update(_parse_link_params(params, replace_chars))
        links.append(link)

    return links