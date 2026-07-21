# === ARP Faza 4C - refactored code ===
# sample_id: requests_014
# condition: A
# timestamp: 2026-06-04T13:31:33
# original_cc: 13, original_mi: None
# changed_pct: 0.8545
# === END HEADER ===
def get_netrc_auth(url, raise_errors=False):
    """Returns the Requests tuple auth for a given url from netrc."""
    netrc_locations = _get_netrc_locations()
    netrc_path = _find_netrc_path(netrc_locations)
    if netrc_path is None:
        return

    try:
        from netrc import NetrcParseError, netrc

        host = _get_host_from_url(url)
        _netrc = netrc(netrc_path).authenticators(host)
        if _netrc:
            login_i = 0 if _netrc[0] else 1
            return (_netrc[login_i], _netrc[2])
    except (NetrcParseError, OSError):
        if raise_errors:
            raise
    except (ImportError, AttributeError):
        pass


def _get_netrc_locations():
    netrc_file = os.environ.get("NETRC")
    if netrc_file is not None:
        return (netrc_file,)
    return (f"~/{f}" for f in NETRC_FILES)


def _find_netrc_path(netrc_locations):
    for f in netrc_locations:
        try:
            loc = os.path.expanduser(f)
        except KeyError:
            return None
        if os.path.exists(loc):
            return loc
    return None


def _get_host_from_url(url):
    ri = urlparse(url)
    splitstr = b":"
    if isinstance(url, str):
        splitstr = splitstr.decode("ascii")
    return ri.netloc.split(splitstr)[0]