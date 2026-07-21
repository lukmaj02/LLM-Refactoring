# SNAPSHOT METADATA
# sample_id: requests_003
# repo: requests
# file: data/repos/requests/src/requests/adapters.py
# function: _urllib3_request_context
# cc: 10 | mi: N/A | loc: 45
# extracted: 2026-05-01T11:47:36

def _urllib3_request_context(
    request: "PreparedRequest",
    verify: "bool | str | None",
    client_cert: "typing.Tuple[str, str] | str | None",
    poolmanager: "PoolManager",
) -> "(typing.Dict[str, typing.Any], typing.Dict[str, typing.Any])":
    host_params = {}
    pool_kwargs = {}
    parsed_request_url = urlparse(request.url)
    scheme = parsed_request_url.scheme.lower()
    port = parsed_request_url.port

    # Determine if we have and should use our default SSLContext
    # to optimize performance on standard requests.
    poolmanager_kwargs = getattr(poolmanager, "connection_pool_kw", {})
    has_poolmanager_ssl_context = poolmanager_kwargs.get("ssl_context")
    should_use_default_ssl_context = (
        _preloaded_ssl_context is not None and not has_poolmanager_ssl_context
    )

    cert_reqs = "CERT_REQUIRED"
    if verify is False:
        cert_reqs = "CERT_NONE"
    elif verify is True and should_use_default_ssl_context:
        pool_kwargs["ssl_context"] = _preloaded_ssl_context
    elif isinstance(verify, str):
        if not os.path.isdir(verify):
            pool_kwargs["ca_certs"] = verify
        else:
            pool_kwargs["ca_cert_dir"] = verify
    pool_kwargs["cert_reqs"] = cert_reqs
    if client_cert is not None:
        if isinstance(client_cert, tuple) and len(client_cert) == 2:
            pool_kwargs["cert_file"] = client_cert[0]
            pool_kwargs["key_file"] = client_cert[1]
        else:
            # According to our docs, we allow users to specify just the client
            # cert path
            pool_kwargs["cert_file"] = client_cert
    host_params = {
        "scheme": scheme,
        "host": parsed_request_url.hostname,
        "port": port,
    }
    return host_params, pool_kwargs
