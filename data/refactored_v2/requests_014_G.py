# === ARP Faza 4C - refactored code ===
# sample_id: requests_014
# condition: G
# timestamp: 2026-06-04T13:32:26
# original_cc: 13, original_mi: None
# changed_pct: 0.8696
# === END HEADER ===
def _get_netrc_locations():
    """Determines the possible paths for netrc files."""
    netrc_file = os.environ.get("NETRC")
    if netrc_file is not None:
        return (netrc_file,)
    return (f"~/{f}" for f in NETRC_FILES)


def _find_existing_netrc_path(netrc_locations):
    """Iterates through netrc locations and returns the first valid path."""
    for f in netrc_locations:
        try:
            loc = os.path.expanduser(f)
        except KeyError:
            # os.path.expanduser can fail when $HOME is undefined and
            # getpwuid fails. See https://bugs.python.org/issue20164 &
            # https://github.com/psf/requests/issues/1846
            return None  # Original behavior: stop searching if expanduser fails
        if os.path.exists(loc):
            return loc
    return None


def _extract_host_from_url(url):
    """Parses the URL and extracts the host without the port."""
    ri = urlparse(url)
    # Strip port numbers from netloc. This weird `if...encode`` dance is
    # used for Python 3.2, which doesn't support unicode literals.
    splitstr = b":"
    if isinstance(url, str):
        splitstr = splitstr.decode("ascii")
    return ri.netloc.split(splitstr)[0]


def _get_netrc_authenticators(netrc_path, host, raise_errors):
    """Reads and parses the netrc file for authenticators for the given host."""
    from netrc import NetrcParseError, netrc

    try:
        _netrc = netrc(netrc_path).authenticators(host)
        if _netrc:
            # Return with login / password
            login_i = 0 if _netrc[0] else 1
            return (_netrc[login_i], _netrc[2])
    except (NetrcParseError, OSError):
        # If there was a parsing error or a permissions issue reading the file,
        # we'll just skip netrc auth unless explicitly asked to raise errors.
        if raise_errors:
            raise
    return None


def get_netrc_auth(url, raise_errors=False):
    """Returns the Requests tuple auth for a given url from netrc."""

    try:
        netrc_locations = _get_netrc_locations()
        netrc_path = _find_existing_netrc_path(netrc_locations)

        if netrc_path is None:
            return None

        host = _extract_host_from_url(url)
        return _get_netrc_authenticators(netrc_path, host, raise_errors)

    # App Engine hackiness.
    except (ImportError, AttributeError):
        pass
    return None