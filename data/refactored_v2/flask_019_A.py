# === ARP Faza 4C - refactored code ===
# sample_id: flask_019
# condition: A
# timestamp: 2026-06-04T14:15:30
# original_cc: 7, original_mi: None
# changed_pct: 0.3962
# === END HEADER ===
def create_url_adapter(self, request: Request | None) -> MapAdapter | None:
    """Creates a URL adapter for the given request. The URL adapter
    is created at a point where the request context is not yet set
    up so the request is passed explicitly.

    .. versionchanged:: 3.1
        If :data:`SERVER_NAME` is set, it does not restrict requests to
        only that domain, for both ``subdomain_matching`` and
        ``host_matching``.

    .. versionchanged:: 1.0
        :data:`SERVER_NAME` no longer implicitly enables subdomain
        matching. Use :attr:`subdomain_matching` instead.

    .. versionchanged:: 0.9
       This can be called outside a request when the URL adapter is created
       for an application context.

    .. versionadded:: 0.6
    """
    if request is not None:
        self._set_request_trusted_hosts(request)
        subdomain, server_name = self._determine_subdomain_and_server_name(request)
        return self.url_map.bind_to_environ(
            request.environ, server_name=server_name, subdomain=subdomain
        )

    return self._bind_outside_request()

def _set_request_trusted_hosts(self, request: Request) -> None:
    if (trusted_hosts := self.config["TRUSTED_HOSTS"]) is not None:
        request.trusted_hosts = trusted_hosts
    request.host = get_host(request.environ, request.trusted_hosts)  # pyright: ignore

def _determine_subdomain_and_server_name(self, request: Request) -> tuple[str | None, str | None]:
    subdomain = None
    server_name = self.config["SERVER_NAME"]

    if self.url_map.host_matching:
        server_name = None
    elif not self.subdomain_matching:
        subdomain = self.url_map.default_subdomain or ""

    return subdomain, server_name

def _bind_outside_request(self) -> MapAdapter | None:
    if self.config["SERVER_NAME"] is not None:
        return self.url_map.bind(
            self.config["SERVER_NAME"],
            script_name=self.config["APPLICATION_ROOT"],
            url_scheme=self.config["PREFERRED_URL_SCHEME"],
        )
    return None