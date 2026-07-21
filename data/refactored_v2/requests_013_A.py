# === ARP Faza 4C - refactored code ===
# sample_id: requests_013
# condition: A
# timestamp: 2026-06-04T13:29:44
# original_cc: 17, original_mi: None
# changed_pct: 0.5424
# === END HEADER ===
def should_bypass_proxies(url, no_proxy):
    """
    Returns whether we should bypass proxies or not.

    :rtype: bool
    """

    def get_proxy(key):
        return os.environ.get(key) or os.environ.get(key.upper())

    def is_bypassed_by_no_proxy(parsed, no_proxy):
        if is_ipv4_address(parsed.hostname):
            return _is_ipv4_bypassed(parsed.hostname, no_proxy)
        return _is_hostname_bypassed(parsed, no_proxy)

    def _is_ipv4_bypassed(hostname, no_proxy):
        for proxy_ip in no_proxy:
            if is_valid_cidr(proxy_ip) and address_in_network(hostname, proxy_ip):
                return True
            if hostname == proxy_ip:
                return True
        return False

    def _is_hostname_bypassed(parsed, no_proxy):
        host_with_port = parsed.hostname
        if parsed.port:
            host_with_port += f":{parsed.port}"
        for host in no_proxy:
            if parsed.hostname.endswith(host) or host_with_port.endswith(host):
                return True
        return False

    no_proxy_arg = no_proxy
    if no_proxy is None:
        no_proxy = get_proxy("no_proxy")
    parsed = urlparse(url)

    if parsed.hostname is None:
        return True

    if no_proxy:
        no_proxy = (host for host in no_proxy.replace(" ", "").split(",") if host)
        if is_bypassed_by_no_proxy(parsed, no_proxy):
            return True

    with set_environ("no_proxy", no_proxy_arg):
        try:
            bypass = proxy_bypass(parsed.hostname)
        except (TypeError, socket.gaierror):
            bypass = False

    return bypass