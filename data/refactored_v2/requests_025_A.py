# === ARP Faza 4C - refactored code ===
# sample_id: requests_025
# condition: A
# timestamp: 2026-06-04T13:44:47
# original_cc: 6, original_mi: None
# changed_pct: 0.3143
# === END HEADER ===
def _parse_link_params(params, replace_chars):
    link_params = {}
    for param in params.split(";"):
        try:
            key, value = param.split("=")
            link_params[key.strip(replace_chars)] = value.strip(replace_chars)
        except ValueError:
            break
    return link_params

def parse_header_links(value):
    """Return a list of parsed link headers proxies.

    i.e. Link: <http:/.../front.jpeg>; rel=front; type="image/jpeg",<http://.../back.jpeg>; rel=back;type="image/jpeg"

    :rtype: list
    """

    links = []
    replace_chars = " '\""
    value = value.strip(replace_chars)
    if not value:
        return links

    for val in re.split(", *<", value):
        try:
            url, params = val.split(";", 1)
        except ValueError:
            url, params = val, ""

        link = {"url": url.strip("<> '\"")}
        link.update(_parse_link_params(params, replace_chars))
        links.append(link)

    return links