# === ARP Faza 4C - refactored code ===
# sample_id: requests_011
# condition: A
# timestamp: 2026-06-04T13:27:29
# original_cc: 10, original_mi: None
# changed_pct: 0.6585
# === END HEADER ===
def should_strip_auth(self, old_url, new_url):
    """Decide whether Authorization header should be removed when redirecting"""
    old_parsed = urlparse(old_url)
    new_parsed = urlparse(new_url)

    if self._hostname_changed(old_parsed, new_parsed):
        return True

    if self._is_http_to_https_standard_port_redirect(old_parsed, new_parsed):
        return False

    if self._is_same_scheme_default_port(old_parsed, new_parsed):
        return False

    return self._has_port_or_scheme_changed(old_parsed, new_parsed)


def _hostname_changed(self, old_parsed, new_parsed):
    return old_parsed.hostname != new_parsed.hostname


def _is_http_to_https_standard_port_redirect(self, old_parsed, new_parsed):
    return (
        old_parsed.scheme == "http"
        and old_parsed.port in (80, None)
        and new_parsed.scheme == "https"
        and new_parsed.port in (443, None)
    )


def _is_same_scheme_default_port(self, old_parsed, new_parsed):
    default_port = (DEFAULT_PORTS.get(old_parsed.scheme, None), None)
    return (
        old_parsed.scheme == new_parsed.scheme
        and old_parsed.port in default_port
        and new_parsed.port in default_port
    )


def _has_port_or_scheme_changed(self, old_parsed, new_parsed):
    return old_parsed.port != new_parsed.port or old_parsed.scheme != new_parsed.scheme