# === ARP Faza 4C - refactored code ===
# sample_id: requests_017
# condition: A
# timestamp: 2026-06-04T13:35:13
# original_cc: 5, original_mi: None
# changed_pct: 0.2308
# === END HEADER ===
def resolve_proxies(request, proxies, trust_env=True):
    """This method takes proxy information from a request and configuration
    input to resolve a mapping of target proxies. This will consider settings
    such as NO_PROXY to strip proxy configurations.

    :param request: Request or PreparedRequest
    :param proxies: A dictionary of schemes or schemes and hosts to proxy URLs
    :param trust_env: Boolean declaring whether to trust environment configs

    :rtype: dict
    """
    proxies = proxies or {}
    url = request.url
    scheme = urlparse(url).scheme
    no_proxy = proxies.get("no_proxy")
    new_proxies = proxies.copy()

    if trust_env and not should_bypass_proxies(url, no_proxy=no_proxy):
        proxy = get_proxy_from_environment(url, scheme, no_proxy)
        if proxy:
            new_proxies.setdefault(scheme, proxy)
    return new_proxies

def get_proxy_from_environment(url, scheme, no_proxy):
    environ_proxies = get_environ_proxies(url, no_proxy=no_proxy)
    return environ_proxies.get(scheme, environ_proxies.get("all"))