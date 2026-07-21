# === ARP Faza 4C - refactored code ===
# sample_id: requests_017
# condition: G
# timestamp: 2026-06-04T13:35:55
# original_cc: 5, original_mi: None
# changed_pct: 0.9200
# === END HEADER ===
def _apply_environ_proxies_to_dict(proxies_dict, url, scheme, no_proxy):
    """
    Applies environment proxies to the given proxies dictionary if applicable.
    Modifies proxies_dict in place using setdefault.
    """
    environ_proxies = get_environ_proxies(url, no_proxy=no_proxy)
    proxy = environ_proxies.get(scheme, environ_proxies.get("all"))
    if proxy:
        proxies_dict.setdefault(scheme, proxy)


def resolve_proxies(request, proxies, trust_env=True):
    """This method takes proxy information from a request and configuration
    input to resolve a mapping of