# === ARP Faza 4C - refactored code ===
# sample_id: requests_006
# condition: C
# timestamp: 2026-06-04T13:24:35
# original_cc: 17, original_mi: None
# changed_pct: 0.5275
# === END HEADER ===
def _normalize_url_string(url):
    """Convert url to a clean string, stripping leading whitespace."""
    if isinstance(url, bytes):
        url = url.decode("utf8")
    else:
        url = str(url)
    return url.lstrip()


def _validate_and_encode_host(host, get_idna_encoded_host):
    """Validate and encode the host, returning the (possibly IDNA-encoded) host."""
    if not unicode_is_ascii(host):
        try:
            host = get_idna_encoded_host(host)
        except UnicodeError:
            raise InvalidURL("URL has an invalid label.")
    elif host.startswith(("*", ".")):
        raise InvalidURL("URL has an invalid label.")
    return host


def _build_netloc(auth, host, port):
    """Reconstruct the network location from its components."""
    netloc = auth or ""
    if netloc:
        netloc += "@"
    netloc += host
    if port:
        netloc += f":{port}"
    return netloc


def _merge_query_params(query, params):
    """Merge encoded params into the existing query string."""
    if not params:
        return query
    if isinstance(params, (str, bytes)):
        params = to_native_string(params)
    enc_params = PreparedRequest._encode_params(params)
    if not enc_params:
        return query
    return f"{query}&{enc_params}" if query else enc_params


def prepare_url(self, url, params):
    """Prepares the given HTTP URL."""
    #: Accept objects that have string representations.
    #: We're unable to blindly call unicode/str functions
    #: as this will include the bytestring indicator (b'')
    #: on python 3.x.
    #: https://github.com/psf/requests/pull/2238
    url = _normalize_url_string(url)

    # Don't do any URL preparation for non-HTTP schemes like `mailto`,
    # `data` etc to work around exceptions from `url_parse`, which
    # handles RFC 3986 only.
    if ":" in url and not url.lower().startswith("http"):
        self.url = url
        return

    # Support for unicode domain names and paths.
    try:
        scheme, auth, host, port, path, query, fragment = parse_url(url)
    except LocationParseError as e:
        raise InvalidURL(*e.args)

    if not scheme:
        raise MissingSchema(
            f"Invalid URL {url!r}: No scheme supplied. "
            f"Perhaps you meant https://{url}?"
        )

    if not host:
        raise InvalidURL(f"Invalid URL {url!r}: No host supplied")

    # In general, we want to try IDNA encoding the hostname if the string contains
    # non-ASCII characters. This allows users to automatically get the correct IDNA
    # behaviour. For strings containing only ASCII characters, we need to also verify
    # it doesn't start with a wildcard (*), before allowing the unencoded hostname.
    host = _validate_and_encode_host(host, self._get_idna_encoded_host)

    netloc = _build_netloc(auth, host, port)

    # Bare domains aren't valid URLs.
    if not path:
        path = "/"

    query = _merge_query_params(query, params)

    url = requote_uri(urlunparse([scheme, netloc, path, None, query, fragment]))
    self.url = url