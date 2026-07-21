# === ARP Faza 4C - refactored code ===
# sample_id: flask_003
# condition: G
# timestamp: 2026-06-04T14:12:17
# original_cc: 12, original_mi: None
# changed_pct: 0.9120
# === END HEADER ===
def _get_url_build_params(
    self,
    endpoint: str,
    _scheme: str | None,
    _external: bool | None,
) -> tuple[MapAdapter, str, bool]:
    """Helper to determine the URL adapter, adjusted endpoint, and final
    _external flag based on the current context.
    """
    req_ctx = _cv_request.get(None)

    if req_ctx is not None:
        url_adapter = req_ctx.url_adapter
        blueprint_name = req_ctx.request.blueprint

        # If the endpoint starts with "." and the request matches a
        # blueprint, the endpoint is relative to the blueprint.
        if endpoint[: