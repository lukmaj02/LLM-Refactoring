# === ARP Faza 4C - refactored code ===
# sample_id: requests_011
# condition: C
# timestamp: 2026-06-04T13:28:51
# original_cc: 10, original_mi: None
# changed_pct: 0.5938
# === END HEADER ===
def _is_http_to_https_upgrade(old_parsed, new_parsed):
    return (
        old_parsed.scheme == "http"
        and old_parsed.port in (80, None)
        and new_parsed.scheme == "https"
        and new_parsed.port in (443, None)
    )


def _ports_are_default_equivalent(old_parsed, new_parsed):
    default_port = (DEFAULT_PORTS.get(old_parsed.scheme, None), None)
    return old_parsed.port in default_port and new_parsed.port in default_port


def should_strip_auth(self, old_url, new_url):
    """Decide whether Authorization header should be removed when redirecting"""
    old_parsed = urlparse(old_url)
    new_parsed = urlparse(new_url)

    if old_parsed.hostname != new_parsed.hostname:
        return True

    if _is_http_to_https_upgrade(old_parsed, new_parsed):
        return False

    changed_port = old_parsed.port != new_parsed.port
    changed_scheme = old_parsed.scheme != new_parsed.scheme

    if not changed_scheme and _ports_are_default_equivalent(old_parsed, new_parsed):
        return False

    return changed_port or changed_scheme