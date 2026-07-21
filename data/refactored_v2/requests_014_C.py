# === ARP Faza 4C - refactored code ===
# sample_id: requests_014
# condition: C
# timestamp: 2026-06-04T13:32:32
# original_cc: 13, original_mi: None
# changed_pct: 0.5965
# === END HEADER ===
def _find_netrc_path(netrc_locations):
    """Find the first existing netrc file from the given locations."""
    for f in netrc_locations:
        try:
            loc = os.path.expanduser(f)
        except KeyError:
            # os.path.expanduser can fail when $HOME is undefined and
            # getpwuid fails. See https://bugs.python.org/issue20164 &
            # https://github.com/psf/requests/issues/1846
            return None
        if os.path.exists(loc):
            return loc
    return None


def _get_netrc_locations():
    """Return the netrc file locations to search."""
    netrc_file = os.environ.get("NETRC")
    if netrc_file is not None:
        return (netrc_file,)
    return (f"~/{f}" for f in NETRC_FILES)


def _extract_host(url):
    """Extract the host (without port) from a URL."""
    ri = urlparse(url)
    splitstr = b":"
    if isinstance(url, str):
        splitstr = splitstr.decode("ascii")
    return ri.netloc.split(splitstr)[0]


def get_netrc_auth(url, raise_errors=False):
    """Returns the Requests tuple auth for a given url from netrc."""
    try:
        from netrc import NetrcParseError, netrc

        netrc_path = _find_netrc_path(_get_netrc_locations())
        if netrc_path is None:
            return

        host = _extract_host(url)

        try:
            _netrc = netrc(netrc_path).authenticators(host)
            if _netrc:
                login_i = 0 if _netrc[0] else 1
                return (_netrc[login_i], _netrc[2])
        except (NetrcParseError, OSError):
            # If there was a parsing error or a permissions issue reading the file,
            # we'll just skip netrc auth unless explicitly asked to raise errors.
            if raise_errors:
                raise

    # App Engine hackiness.
    except (ImportError, AttributeError):
        pass