# === ARP Faza 4C - refactored code ===
# sample_id: requests_009
# condition: A
# timestamp: 2026-06-04T13:26:28
# original_cc: 15, original_mi: None
# changed_pct: 0.3361
# === END HEADER ===
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
        hist.append(resp)
        resp.history = hist[1:]

        _consume_response_content(resp)

        if len(resp.history) >= self.max_redirects:
            raise TooManyRedirects(
                f"Exceeded {self.max_redirects} redirects.", response=resp
            )

        resp.close()

        url = _normalize_url(url, resp, previous_fragment)
        previous_fragment = urlparse(url).fragment or previous_fragment

        prepared_request.url = to_native_string(url)

        self.rebuild_method(prepared_request, resp)

        if resp.status_code not in (
            codes.temporary_redirect,
            codes.permanent_redirect,
        ):
            _purge_headers(prepared_request)
            prepared_request.body = None

        headers = prepared_request.headers
        headers.pop("Cookie", None)

        extract_cookies_to_jar(prepared_request._cookies, req, resp.raw)
        merge_cookies(prepared_request._cookies, self.cookies)
        prepared_request.prepare_cookies(prepared_request._cookies)

        proxies = self.rebuild_proxies(prepared_request, proxies)
        self.rebuild_auth(prepared_request, resp)

        rewindable = prepared_request._body_position is not None and (
            "Content-Length" in headers or "Transfer-Encoding" in headers
        )

        if rewindable:
            rewind_body(prepared_request)

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

            url = self.get_redirect_target(resp)
            yield resp


def _consume_response_content(resp):
    try:
        resp.content
    except (ChunkedEncodingError, ContentDecodingError, RuntimeError):
        resp.raw.read(decode_content=False)


def _normalize_url(url, resp, previous_fragment):
    if url.startswith("//"):
        parsed_rurl = urlparse(resp.url)
        url = ":".join([to_native_string(parsed_rurl.scheme), url])

    parsed = urlparse(url)
    if parsed.fragment == "" and previous_fragment:
        parsed = parsed._replace(fragment=previous_fragment)
    return parsed.geturl() if parsed.netloc else urljoin(resp.url, requote_uri(url))


def _purge_headers(prepared_request):
    purged_headers = ("Content-Length", "Content-Type", "Transfer-Encoding")
    for header in purged_headers:
        prepared_request.headers.pop(header, None)