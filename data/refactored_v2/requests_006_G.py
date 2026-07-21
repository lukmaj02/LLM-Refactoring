# === ARP Faza 4C - refactored code ===
# sample_id: requests_006
# condition: G
# timestamp: 2026-06-04T13:25:54
# original_cc: 17, original_mi: None
# changed_pct: 0.5816
# === END HEADER ===
def _normalize_url_string(self, url):
    """Accepts objects that have string representations and removes leading whitespace."""
    if isinstance(url, bytes):
        url = url.decode("utf8")
    else:
        url = str(url)
    return url.lstrip()

def _handle_non_http_scheme(self, url):
    """
    Checks if the URL uses a non-HTTP scheme and, if so, sets self.url and returns True.
    This works around exceptions from `url_parse`, which handles RFC 3986 only.
    """
    if ":" in url and not url.lower().startswith("http"):
        self.url = url
        return True
    return False

def _parse_and_validate_url_components(self, url):
    """
    Parses the URL into its components and validates the scheme and host.
    Raises InvalidURL or MissingSchema on validation failure.
    """
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

    return scheme, auth, host, port, path, query, fragment

def _prepare_host_for_url(self, host):
    """
    Applies IDNA encoding to the host if it contains non-ASCII characters,
    and validates the host against invalid labels.
    """
    if not unicode_is_ascii(host):
        try:
            host = self._get_idna_encoded_host(host)
        except UnicodeError:
            raise InvalidURL("URL has an invalid label.")
    elif host.startswith(("*", ".")):
        raise InvalidURL("URL has an invalid label.")
    return host

def _build_netloc_string(self, auth, host, port):
    """Reconstructs the network location string from its components."""
    netloc = auth or ""
    if netloc:
        netloc += "@"
    netloc += host
    if port:
        netloc += f":{port}"
    return netloc

def _prepare_query_string(self, current_query, params):
    """
    Encodes parameters and appends them to the existing query string.
    """
    if isinstance(params, (str, bytes)):
        params = to_native_string(params)

    encoded_params = self._encode_params(params)

    if encoded_params:
        if current_query:
            return f"{current_query}&{encoded_params}"
        else:
            return encoded_params
    return current_query

def prepare_url(self, url, params):
    """Prepares the given HTTP URL."""
    url = self._normalize_url_string(url)

    if self._handle_non_http_scheme(url):
        return

    scheme, auth, host, port, path, query, fragment = self._parse_and_validate_url_components(url)

    host = self._prepare_host_for_url(host)

    netloc = self._build_netloc_string(auth, host, port)

    # Bare domains aren't valid URLs.
    path = path or "/"

    query = self._prepare_query_string(query, params)

    final_url = requote_uri(urlunparse([scheme, netloc, path, None, query, fragment]))
    self.url = final_url