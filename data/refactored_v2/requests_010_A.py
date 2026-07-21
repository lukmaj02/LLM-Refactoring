# === ARP Faza 4C - refactored code ===
# sample_id: requests_010
# condition: A
# timestamp: 2026-06-04T13:26:50
# original_cc: 11, original_mi: None
# changed_pct: 0.7763
# === END HEADER ===
def send(self, request, **kwargs):
    """Send a given PreparedRequest.

    :rtype: requests.Response
    """
    self._set_default_kwargs(kwargs)
    self._validate_request_type(request)

    allow_redirects = kwargs.pop("allow_redirects", True)
    stream = kwargs.get("stream")
    hooks = request.hooks

    adapter = self.get_adapter(url=request.url)
    start = preferred_clock()

    r = adapter.send(request, **kwargs)
    r.elapsed = timedelta(seconds=preferred_clock() - start)

    r = dispatch_hook("response", hooks, r, **kwargs)
    self._persist_cookies(r, request)

    history = self._handle_redirects(r, request, allow_redirects, **kwargs)

    if history:
        r = self._update_response_with_history(r, history)

    if not allow_redirects:
        self._set_next_response(r, request, **kwargs)

    if not stream:
        r.content

    return r

def _set_default_kwargs(self, kwargs):
    kwargs.setdefault("stream", self.stream)
    kwargs.setdefault("verify", self.verify)
    kwargs.setdefault("cert", self.cert)
    if "proxies" not in kwargs:
        kwargs["proxies"] = resolve_proxies(request, self.proxies, self.trust_env)

def _validate_request_type(self, request):
    if isinstance(request, Request):
        raise ValueError("You can only send PreparedRequests.")

def _persist_cookies(self, response, request):
    if response.history:
        for resp in response.history:
            extract_cookies_to_jar(self.cookies, resp.request, resp.raw)
    extract_cookies_to_jar(self.cookies, request, response.raw)

def _handle_redirects(self, response, request, allow_redirects, **kwargs):
    if allow_redirects:
        gen = self.resolve_redirects(response, request, **kwargs)
        return [resp for resp in gen]
    return []

def _update_response_with_history(self, response, history):
    history.insert(0, response)
    response = history.pop()
    response.history = history
    return response

def _set_next_response(self, response, request, **kwargs):
    try:
        response._next = next(
            self.resolve_redirects(response, request, yield_requests=True, **kwargs)
        )
    except StopIteration:
        pass