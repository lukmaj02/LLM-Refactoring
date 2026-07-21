# === ARP Faza 4C - refactored code ===
# sample_id: requests_011
# condition: G
# timestamp: 2026-06-04T13:28:49
# original_cc: 10, original_mi: None
# changed_pct: 0.5581
# === END HEADER ===
def should_strip_auth(self, old_url, new_url):
    """Decide whether Authorization header should be removed when redirecting"""
    old_parsed = urlparse(old_url)
    new_parsed = urlparse(new_url)

    if self._is_different_hostname(old_parsed, new_parsed):
        return True

    # Special case: allow http -> https redirect when using the standard
    # ports. This isn't specified by RFC 7235, but is kept to avoid
    # breaking backwards compatibility with older versions of requests
    # that allowed any redirects on the same host.
    if self._is_http_to_https_standard_port_redirect(old_parsed, new_parsed):
        return False

    # Handle default port usage corresponding to scheme.
    if self._is_same_scheme_default_port_redirect(old_parsed, new_parsed):
        return False

    # Standard case: root URI must match
    changed_port = old_parsed.port != new_parsed.port
    changed_scheme = old_parsed.scheme != new_parsed.scheme
    return changed_port or changed_scheme

def _is_different_hostname(self, old_parsed, new_parsed):
    return old_parsed.hostname != new_parsed.hostname

def _is_http_to_https_standard_port_redirect(self, old_parsed, new_parsed):
    return (
        old_parsed.scheme == "http"
        and old_parsed.port in (80, None)
        and new_parsed.scheme == "https"
        and new_parsed.port in (443, None)
    )

def _is_same_scheme_default_port_redirect(self, old_parsed, new_parsed):
    changed_scheme = old_parsed.scheme != new_parsed.scheme
    default_port = (DEFAULT_PORTS.get(old_parsed.scheme, None), None)
    return (
        not changed_scheme
        and old_parsed.port in default_port
        and new_parsed.port in default_port
    )