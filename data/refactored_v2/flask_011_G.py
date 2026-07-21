# === ARP Faza 4C - refactored code ===
# sample_id: flask_011
# condition: G
# timestamp: 2026-06-04T14:16:10
# original_cc: 13, original_mi: None
# changed_pct: 0.9298
# === END HEADER ===
def _get_or_create_endpoint(
    endpoint: str | None, view_func: ft.RouteCallable | None
) -> str:
    if endpoint is None:
        return _endpoint_from_view_func(view_func)  # type: ignore
    return endpoint


def _normalize_methods(
    methods_raw: t.Any, view_func: ft.RouteCallable | None
) -> set[str]:
    if methods_raw is None:
        methods_raw = getattr(view_func, "methods", None) or ("GET",)
    if isinstance(methods_raw, str):
        raise TypeError(
            "Allowed methods must be a list of strings, for"
            ' example