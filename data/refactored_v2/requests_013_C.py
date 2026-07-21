# === ARP Faza 4C - refactored code ===
# sample_id: requests_013
# condition: C
# timestamp: 2026-06-04T13:30:59
# original_cc: 17, original_mi: None
# changed_pct: 0.6866
# === END HEADER ===
def _get_proxy_env(key):
    """Prioritize lowercase environment variables over uppercase."""
    return os.environ.get(key) or os.environ.get(key.upper())


def _hostname_matches_no_proxy_ip(hostname, no_proxy_list):
    """Check if an IPv4 hostname matches any entry in the no_proxy list."""
    for proxy_ip in no_proxy_list:
        if is_valid_cidr(proxy_ip):
            if address_in_network(hostname, proxy_ip):
                return True
        elif hostname == proxy_ip:
            return True
    return False


def _hostname_matches_no_proxy_host(parsed, no_proxy_list):
    """Check if a non-IP hostname matches any entry in the no_proxy list."""
    host_with_port = parsed.hostname
    if parsed.port:
        host_with_port += f":{parsed.port}"

    for host in no_proxy_list:
        if parsed.hostname.endswith(host) or host_with_port.endswith(host):
            return True
    return False


def _matches_no_proxy(parsed, no_proxy):
    """Return True if the parsed URL matches any entry in the no_proxy string."""
    if not no_proxy:
        return False

    no_proxy_list = [h for h in no_proxy.replace(" ", "").split(",") if h]

    if is_ipv4_address(parsed.hostname):
        return _hostname_matches_no_proxy_ip(parsed.hostname, no_proxy_list)
    else:
        return _hostname_matches_no_proxy_host(parsed, no_proxy_list)


def should_bypass_proxies(url, no_proxy):
    """
    Returns whether we should bypass proxies or not.

    :rtype: bool
    """
    no_proxy_arg = no_proxy
    if no_proxy is None:
        no_proxy = _get_proxy_env("no_proxy")

    parsed = urlparse(url)

    if parsed.hostname is None:
        # URLs don't always have hostnames, e.g. file:/// urls.
        return True

    if _matches_no_proxy(parsed, no_proxy):
        return True

    with set_environ("no_proxy", no_proxy_arg):
        try:
            bypass = proxy_bypass(parsed.hostname)
        except (TypeError, socket.gaierror):
            bypass = False

    return bool(bypass)