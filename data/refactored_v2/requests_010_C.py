# === ARP Faza 4C - refactored code ===
# sample_id: requests_010
# condition: C
# timestamp: 2026-06-04T13:28:08
# original_cc: 11, original_mi: None
# changed_pct: 0.5658
# === END HEADER ===
def _set_send_defaults(self, request, kwargs):
    kwargs.setdefault("stream", self.stream)
    kwargs.setdefault("verify", self.verify)
    kwargs.setdefault("cert", self.cert)
    if "proxies" not in kwargs:
        kwargs["proxies"] = resolve_proxies(request, self.proxies, self.trust_env)


def _dispatch_and_persist_cookies(self, request, r, **kwargs):
    r = dispatch_hook("response", r.hooks if hasattr(r, 'hooks') else request.hooks, r, **kwargs)
    if r.history:
        for resp in r.history:
            extract_cookies_to_jar(self.cookies, resp.request, resp.raw)
    extract_cookies_to_jar(self.cookies, request, r.raw)
    return r


def _resolve_redirect_history(self, r, request, allow_redirects, **kwargs):
    if allow_redirects:
        history = list(self.resolve_redirects(r, request, **kwargs))
    else:
        history = []

    if history:
        history.insert(0, r)
        r = history.pop()
        r.history = history

    if not allow_redirects:
        try:
            r._next = next(
                self.resolve_redirects(r, request, yield_requests=True, **kwargs)
            )
        except StopIteration:
            pass

    return r


def send(self, request, **kwargs):
    """Send a given PreparedRequest.

    :rtype: requests.Response
    """
    self._set_send_defaults(request, kwargs)

    if isinstance(request, Request):
        raise ValueError("You can only send PreparedRequests.")

    allow_redirects = kwargs.pop("allow_redirects", True)
    stream = kwargs.get("stream")
    hooks = request.hooks

    adapter = self.get_adapter(url=request.url)

    start = preferred_clock()
    r = adapter.send(request, **kwargs)
    r.elapsed = timedelta(seconds=preferred_clock() - start)

    r = dispatch_hook("response", hooks, r, **kwargs)

    if r.history:
        for resp in r.history:
            extract_cookies_to_jar(self.cookies, resp.request, resp.raw)
    extract_cookies_to_jar(self.cookies, request, r.raw)

    r = self._resolve_redirect_history(r, request, allow_redirects, **kwargs)

    if not stream:
        r.content

    return r