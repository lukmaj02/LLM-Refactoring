# === ARP Faza 4C - refactored code ===
# sample_id: requests_025
# condition: G
# timestamp: 2026-06-04T13:43:20
# original_cc: 6, original_mi: None
# changed_pct: 0.5814
# === END HEADER ===
def _parse_single_link_header(link_string, replace_chars):
    """Helper to parse a single link header string into a dictionary."""
    try:
        url_part, params_part = link_string.split(";", 1)
    except ValueError:
        url_part, params_part = link_string, ""

    link = {"url": url_part.strip("<> '\"")}

    for param in params_part.split(";"):
        try:
            key, value = param.split("=")
        except ValueError:
            # If a parameter cannot be split into key=value,
            # the original behavior was to break and ignore subsequent parameters.
            break
        link[key.strip(replace_chars)] = value.strip(replace_chars)
    return link


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

    # Split the header value into individual link strings.
    # The regex handles optional spaces after the comma and before the '<'.
    link_strings = re.split(", *<", value)

    for link_string in link_strings:
        link = _parse_single_link_header(link_string, replace_chars)
        links.append(link)

    return links