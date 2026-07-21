# === ARP Faza 4C - refactored code ===
# sample_id: requests_009
# condition: C
# timestamp: 2026-06-04T13:26:42
# original_cc: 15, original_mi: None
# changed_pct: 0.4351
# === END HEADER ===
def _resolve_redirect_url(self, url, resp, previous_fragment):
    """Normalize and resolve a redirect URL, returning (url, previous_fragment)."""
    # Handle redirection without scheme (see: RFC 1808 Section 4)
    if url.startswith("//"):
        parsed_rurl = urlparse(resp.url)
        url = ":".join([to_native_string(parsed_rurl.scheme), url])

    # Normalize url case and attach previous fragment if needed (RFC 7231 7.1.2)
    parsed = urlparse(url)
    if parsed.fragment == "" and previous_fragment:
        parsed = parsed._replace(fragment=previous_fragment)
    elif parsed.fragment:
        previous_fragment = parsed.fragment
    url = parsed.geturl()

    # Facilitate relative 'location' headers, as allowed by RFC 7231.
    # Compliant with RFC3986, we percent encode the url.
    if not parsed.netloc:
        url = urljoin(resp.url, requote_uri(url))
    else:
        url = requote_uri(url)

    return to_native_string(url), previous_fragment


def _prepare_redirect_request(self, prepared_request, resp, req, proxies):
    """Mutate prepared_request in-place for the redirect, return updated proxies."""
    self.rebuild_method(prepared_request, resp)

    # https://github.com/psf/requests/issues/1084
    if resp.status_code not in (codes.temporary_redirect, codes.permanent_redirect):
        # https://github.com/psf/requests/issues/3490
        purged_headers = ("Content-Length", "Content-Type", "Transfer-Encoding")
        for header in purged_headers:
            prepared_request.headers.pop(header, None)
        prepared_request.body = None

    prepared_request.headers.pop("Cookie", None)

    # Extract any cookies sent on the response to the cookiejar
    # in the new request. Because we've mutated our copied prepared
    # request, use the old one that we haven't yet touched.
    extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
    merge_cookies(prepared_request._cookies, self.cookies)
    prepared_request.prepare_cookies(prepared_request._cookies)

    # Rebuild auth and proxy information.
    proxies = self.rebuild_proxies(prepared_request, proxies)
    self.rebuild_auth(prepared_request, resp)

    return proxies


def resolve_redirects(
    self,
    resp,
    req,
    stream=False,
    timeout=None,
    verify=True,
    cert=None,
    proxies=None,
    yield_requests=False,
    **adapter_kwargs,
):
    """Receives a Response. Returns a generator of Responses or Requests."""

    hist = []  # keep track of history

    url = self.get_redirect_target(resp)
    previous_fragment = urlparse(req.url).fragment
    while url:
        prepared_request = req.copy()

        # Update history and keep track of redirects.
        # resp.history must ignore the original request in this loop
        hist.append(resp)
        resp.history = hist[1:]

        try:
            resp.content  # Consume socket so it can be released
        except (ChunkedEncodingError, ContentDecodingError, RuntimeError):
            resp.raw.read(decode_content=False)

        if len(resp.history) >= self.max_redirects:
            raise TooManyRedirects(
                f"Exceeded {self.max_redirects} redirects.", response=resp
            )

        # Release the connection back into the pool.
        resp.close()

        url, previous_fragment = self._resolve_redirect_url(url, resp, previous_fragment)
        prepared_request.url = url

        proxies = self._prepare_redirect_request(prepared_request, resp, req, proxies)

        # A failed tell() sets `_body_position` to `object()`. This non-None
        # value ensures `rewindable` will be True, allowing us to raise an
        # UnrewindableBodyError, instead of hanging the connection.
        headers = prepared_request.headers
        rewindable = prepared_request._body_position is not None and (
            "Content-Length" in headers or "Transfer-Encoding" in headers
        )

        # Attempt to rewind consumed file-like object.
        if rewindable:
            rewind_body(prepared_request)

        # Override the original request.
        req = prepared_request

        if yield_requests:
            yield req
        else:
            resp = self.send(
                req,
                stream=stream,
                timeout=timeout,
                verify=verify,
                cert=cert,
                proxies=proxies,
                allow_redirects=False,
                **adapter_kwargs,
            )

            extract_cookies_to_jar(self.cookies, prepared_request, resp.raw)

            # extract redirect url, if any, for the next loop
            url = self.get_redirect_target(resp)
            yield resp