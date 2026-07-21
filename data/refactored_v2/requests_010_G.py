# === ARP Faza 4C - refactored code ===
# sample_id: requests_010
# condition: G
# timestamp: 2026-06-04T13:28:37
# original_cc: 11, original_mi: None
# changed_pct: 0.8421
# === END HEADER ===
def _prepare_send_kwargs(self, request, kwargs):
        """Sets default values for stream, verify, cert, and resolves proxies."""
        kwargs.setdefault("stream", self.stream)
        kwargs.setdefault("verify", self.verify)
        kwargs.setdefault("cert", self.cert)
        if "proxies" not in kwargs:
            kwargs["proxies"] = resolve_proxies(request, self.proxies, self.trust_env)
        return kwargs

    def _send_request_and_dispatch_hooks(self, request, adapter, hooks, **kwargs):
        """Sends the request, measures elapsed time, and dispatches response hooks."""
        start = preferred_clock()
        r = adapter.send(request, **kwargs)
        elapsed = preferred_clock() - start
        r.elapsed = timedelta(seconds=elapsed)
        r = dispatch_hook("response", hooks, r, **kwargs)
        return r

    def _persist_response_cookies(self, request, response):
        """Extracts and merges cookies from the response and its history."""
        if response.history:
            for resp in response.history:
                extract_cookies_to_jar(self.cookies, resp.request, resp.raw)
        extract_cookies_to_jar(self.cookies, request, response.raw)

    def _handle_redirects_and_history(self, initial_response, initial_request, allow_redirects, **kwargs):
        """Resolves redirects and updates the response history."""
        r = initial_response

        if allow_redirects:
            gen = self.resolve_redirects(r, initial_request, **kwargs)
            history = [resp for resp in gen]

            if history:
                # Insert the first (original) request at the start
                history.insert(0, r)
                # Get the last request made
                r = history.pop()
                r.history = history
        else:
            # If redirects aren't being followed, store the response on the Request for Response.next().
            try:
                r._next = next(
                    self.resolve_redirects(r, initial_request, yield_requests=True, **kwargs)
                )
            except StopIteration:
                pass
        return r

    def send(self, request, **kwargs):
        """Send a given PreparedRequest.

        :rtype: requests.Response
        """
        # It's possible that users might accidentally send a Request object.
        # Guard against that specific failure case.
        if isinstance(request, Request):
            raise ValueError("You can only send PreparedRequests.")

        # Set defaults that the hooks can utilize to ensure they always have
        # the correct parameters to reproduce the previous request.
        kwargs = self._prepare_send_kwargs(request, kwargs)

        allow_redirects = kwargs.pop("allow_redirects", True)
        stream = kwargs.get("stream")
        hooks = request.hooks

        # Get the appropriate adapter to use
        adapter = self.get_adapter(url=request.url)

        # Send the request and dispatch hooks
        r = self._send_request_and_dispatch_hooks(request, adapter, hooks, **kwargs)

        # Persist