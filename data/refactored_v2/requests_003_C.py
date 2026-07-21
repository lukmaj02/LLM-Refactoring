# === ARP Faza 4C - refactored code ===
# sample_id: requests_003
# condition: C
# timestamp: 2026-06-04T13:21:35
# original_cc: 10, original_mi: None
# changed_pct: 0.6154
# === END HEADER ===
def _should_use_default_ssl_context(poolmanager):
    poolmanager_kwargs = getattr(poolmanager, "connection_pool_kw", {})
    has_poolmanager_ssl_context = poolmanager_kwargs.get("ssl_context")
    return _preloaded_ssl_context is not None and not has_poolmanager_ssl_context


def _resolve_verify_kwargs(verify, should_use_default_ssl_context):
    pool_kwargs = {}
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
    return pool_kwargs


def _resolve_client_cert_kwargs(client_cert):
    if client_cert is None:
        return {}
    if isinstance(client_cert, tuple) and len(client_cert) == 2:
        return {"cert_file": client_cert[0], "key_file": client_cert[1]}
    # According to our docs, we allow users to specify just the client cert path
    return {"cert_file": client_cert}


def _urllib3_request_context(
    request: "PreparedRequest",
    verify: "bool | str | None",
    client_cert: "typing.Tuple[str, str] | str | None",
    poolmanager: "PoolManager",
) -> "(typing.Dict[str, typing.Any], typing.Dict[str, typing.Any])":
    parsed_request_url = urlparse(request.url)
    scheme = parsed_request_url.scheme.lower()
    port = parsed_request_url.port

    pool_kwargs = _resolve_verify_kwargs(verify, _should_use_default_ssl_context(poolmanager))
    pool_kwargs.update(_resolve_client_cert_kwargs(client_cert))

    host_params = {
        "scheme": scheme,
        "host": parsed_request_url.hostname,
        "port": port,
    }
    return host_params, pool_kwargs