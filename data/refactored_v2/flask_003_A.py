# === ARP Faza 4C - refactored code ===
# sample_id: flask_003
# condition: A
# timestamp: 2026-06-04T14:10:39
# original_cc: 12, original_mi: None
# changed_pct: 0.6240
# === END HEADER ===
def url_for(
    self,
    /,
    endpoint: str,
    *,
    _anchor: str | None = None,
    _method: str | None = None,
    _scheme: str | None = None,
    _external: bool | None = None,
    **values: t.Any,
) -> str:
    req_ctx = _cv_request.get(None)
    url_adapter, _external = self._get_url_adapter_and_external(
        req_ctx, _scheme, _external
    )

    if req_ctx is not None:
        blueprint_name = req_ctx.request.blueprint
        endpoint = self._resolve_endpoint(endpoint, blueprint_name)
    else:
        if url_adapter is None:
            raise RuntimeError(
                "Unable to build URLs outside an active request"
                " without 'SERVER_NAME' configured. Also configure"
                " 'APPLICATION_ROOT' and 'PREFERRED_URL_SCHEME' as"
                " needed."
            )

    if _scheme is not None and not _external:
        raise ValueError("When specifying '_scheme', '_external' must be True.")

    self.inject_url_defaults(endpoint, values)

    try:
        rv = url_adapter.build(
            endpoint,
            values,
            method=_method,
            url_scheme=_scheme,
            force_external=_external,
        )
    except BuildError as error:
        values.update(
            _anchor=_anchor, _method=_method, _scheme=_scheme, _external=_external
        )
        return self.handle_url_build_error(error, endpoint, values)

    if _anchor is not None:
        _anchor = _url_quote(_anchor, safe="%!#$&'()*+,/:;=?@")
        rv = f"{rv}#{_anchor}"

    return rv


def _get_url_adapter_and_external(self, req_ctx, _scheme, _external):
    if req_ctx is not None:
        url_adapter = req_ctx.url_adapter
        if _external is None:
            _external = _scheme is not None
    else:
        app_ctx = _cv_app.get(None)
        url_adapter = app_ctx.url_adapter if app_ctx is not None else self.create_url_adapter(None)
        if _external is None:
            _external = True
    return url_adapter, _external


def _resolve_endpoint(self, endpoint, blueprint_name):
    if endpoint[:1] == ".":
        if blueprint_name is not None:
            endpoint = f"{blueprint_name}{endpoint}"
        else:
            endpoint = endpoint[1:]
    return endpoint