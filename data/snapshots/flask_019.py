# SNAPSHOT METADATA
# sample_id: flask_019
# repo: flask
# file: data/repos/flask/src/flask/app.py
# function: Flask.create_url_adapter
# cc: 7 | mi: N/A | loc: 52
# extracted: 2026-05-01T11:47:37

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
        if (trusted_hosts := self.config["TRUSTED_HOSTS"]) is not None:
            request.trusted_hosts = trusted_hosts

        # Check trusted_hosts here until bind_to_environ does.
        request.host = get_host(request.environ, request.trusted_hosts)  # pyright: ignore
        subdomain = None
        server_name = self.config["SERVER_NAME"]

        if self.url_map.host_matching:
            # Don't pass SERVER_NAME, otherwise it's used and the actual
            # host is ignored, which breaks host matching.
            server_name = None
        elif not self.subdomain_matching:
            # Werkzeug doesn't implement subdomain matching yet. Until then,
            # disable it by forcing the current subdomain to the default, or
            # the empty string.
            subdomain = self.url_map.default_subdomain or ""

        return self.url_map.bind_to_environ(
            request.environ, server_name=server_name, subdomain=subdomain
        )

    # Need at least SERVER_NAME to match/build outside a request.
    if self.config["SERVER_NAME"] is not None:
        return self.url_map.bind(
            self.config["SERVER_NAME"],
            script_name=self.config["APPLICATION_ROOT"],
            url_scheme=self.config["PREFERRED_URL_SCHEME"],
        )

    return None
