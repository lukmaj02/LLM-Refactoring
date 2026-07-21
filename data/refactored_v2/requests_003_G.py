# === ARP Faza 4C - refactored code ===
# sample_id: requests_003
# condition: G
# timestamp: 2026-06-04T13:22:01
# original_cc: 10, original_mi: None
# changed_pct: 0.7246
# === END HEADER ===
def _get_ssl_verify_kwargs(
    verify: "bool | str | None", should_use_default_ssl_context: bool
) -> "typing.Dict[str, typing.Any]":
    """
    Determines the SSL verification related keyword arguments for urllib3's
    connection pool based on the 'verify' parameter.
    """
    ssl_kwargs = {"cert_reqs": "CERT_REQUIRED"}  # Default
    if verify is False:
        ssl_kwargs["cert_reqs"] = "CERT_NONE"
    elif verify is True and should_use_default_ssl_context:
        ssl_kwargs["ssl_context"] = _preloaded_ssl_context
    elif isinstance(verify, str):
        if not os.path.isdir(verify):
            ssl_kwargs["ca_certs"] = verify
        else:
            ssl_kwargs["ca_cert_dir"] = verify
    return ssl_kwargs


def _get_client_cert_kwargs(
    client_cert: "typing.Tuple[str, str] | str | None",
) -> "typing.Dict[str, typing.Any]":
    """
    Determines the client certificate related keyword arguments for urllib3's
    connection pool based on the 'client_cert' parameter.
    """
    cert_kwargs = {}
    if client_cert is not None:
        if isinstance(client_cert, tuple) and len(client_cert) == 2:
            cert_kwargs["cert_file"] = client_cert[0]
            cert_kwargs["key_file"] = client_cert[1]
        else:
            # According to our docs, we allow users to specify just the client
            # cert path
            cert_kwargs["cert_file"] = client_cert
    return cert_kwargs


def _urllib3_request_context(
    request: "PreparedRequest",
    verify: "bool | str | None",
    client_cert: "typing.Tuple[str, str] | str | None",
    poolmanager: "PoolManager",
) -> "(typing.Dict[str, typing.Any], typing.Dict[str, typing.Any])":
    parsed_request_url = urlparse(request.url)
    scheme = parsed_request_url.scheme.lower()
    port = parsed_request_url.port

    host_params = {
        "scheme": scheme,
        "host": parsed_request_url.hostname,
        "port": port,
    }

    pool_kwargs = {}

    # Determine if we have and should use our default SSLContext
    # to optimize performance on standard requests.
    poolmanager_kwargs = getattr(poolmanager, "connection_pool_kw", {})
    has_poolmanager_ssl_context = poolmanager_kwargs.get("ssl_context")
    should_use_default_ssl_context = (
        _preloaded_ssl_context is not None and not has_poolmanager_ssl_context
    )

    pool_kwargs.update(_get_ssl_verify_kwargs(verify, should_use_default_ssl_context))
    pool_kwargs.update(_get_client_cert_kwargs(client_cert))

    return host_params, pool_kwargs