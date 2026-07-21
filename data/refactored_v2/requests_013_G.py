# === ARP Faza 4C - refactored code ===
# sample_id: requests_013
# condition: G
# timestamp: 2026-06-04T13:30:50
# original_cc: 17, original_mi: None
# changed_pct: 0.6667
# === END HEADER ===
def _get_proxy_from_env(key):
    """Prioritize lowercase environment variables over uppercase."""
    return os.environ.get(key) or os.environ.get(key.upper())


def _matches_no_proxy_list(hostname, port, no_proxy_list_str):
    """
    Checks if the given hostname (with optional port) matches any entry
    in the no_proxy list string.
    """
    if not no_proxy_list_str:
        return False

    no_proxy_entries = (
        host for host in no_proxy_list_str.replace(" ", "").split(",") if host
    )

    if is_ipv4_address(hostname):
        for proxy_ip in no_proxy_entries:
            if is_valid_cidr(proxy_ip):
                if address_in_network(hostname, proxy_ip):
                    return True
            elif hostname == proxy_ip:
                # If no_proxy ip was defined in plain IP notation instead of cidr notation &
                # matches the IP of the index
                return True
    else:
        host_with_port = hostname
        if port:
            host_with_port += f":{port}"

        for host_entry in no_proxy_entries:
            if hostname.endswith(host_entry) or host_with_port.endswith(host_entry):
                # The URL does match something in no_proxy, so we don't want
                # to apply the proxies on this URL.
                return True
    return False


def should_bypass_proxies(url, no_proxy):
    """
    Returns whether we should bypass proxies or not.

    :rtype: bool
    """
    original_no_proxy_arg = no_proxy

    # First check whether no_proxy is defined. If it is, check that the URL
    # we're getting isn't in the no_proxy list.
    if no_proxy is None:
        no_proxy = _get_proxy_from_env("no_proxy")

    parsed = urlparse(url)

    if parsed.hostname is None:
        # URLs don't always have hostnames, e.g. file:/// urls.
        return True

    if _matches_no_proxy_list(parsed.hostname, parsed.port, no_proxy):
        return True

    with set_environ("no_proxy", original_no_proxy_arg):
        # parsed.hostname can be `None` in cases such as a file URI.
        try:
            bypass = proxy_bypass(parsed.hostname)
        except (TypeError, socket.gaierror):
            bypass = False

    return bypass