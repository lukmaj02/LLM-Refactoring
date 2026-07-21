# === ARP Faza 4C - refactored code ===
# sample_id: requests_006
# condition: A
# timestamp: 2026-06-04T13:24:43
# original_cc: 17, original_mi: None
# changed_pct: 0.5753
# === END HEADER ===
def prepare_url(self, url, params):
    """Prepares the given HTTP URL."""
    url = self._decode_url(url)
    url = url.lstrip()

    if self._is_non_http_scheme(url):
        self.url = url
        return

    scheme, auth, host, port, path, query, fragment = self._parse_url(url)

    host = self._validate_and_encode_host(host)

    netloc = self._construct_netloc(auth, host, port)
    path = path or "/"

    enc_params = self._encode_params(params)
    query = self._construct_query(query, enc_params)

    self.url = requote_uri(urlunparse([scheme, netloc, path, None, query, fragment]))


def _decode_url(self, url):
    if isinstance(url, bytes):
        return url.decode("utf8")
    return str(url)


def _is_non_http_scheme(self, url):
    return ":" in url and not url.lower().startswith("http")


def _parse_url(self, url):
    try:
        return parse_url(url)
    except LocationParseError as e:
        raise InvalidURL(*e.args)


def _validate_and_encode_host(self, host):
    if not host:
        raise InvalidURL("Invalid URL: No host supplied")

    if not unicode_is_ascii(host):
        try:
            return self._get_idna_encoded_host(host)
        except UnicodeError:
            raise InvalidURL("URL has an invalid label.")
    elif host.startswith(("*", ".")):
        raise InvalidURL("URL has an invalid label.")

    return host


def _construct_netloc(self, auth, host, port):
    netloc = auth or ""
    if netloc:
        netloc += "@"
    netloc += host
    if port:
        netloc += f":{port}"
    return netloc


def _construct_query(self, query, enc_params):
    if enc_params:
        if query:
            return f"{query}&{enc_params}"
        return enc_params
    return query