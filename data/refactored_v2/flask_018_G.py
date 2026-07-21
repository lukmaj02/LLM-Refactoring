# === ARP Faza 4C - refactored code ===
# sample_id: flask_018
# condition: G
# timestamp: 2026-06-04T14:18:31
# original_cc: 7, original_mi: None
# changed_pct: 0.7917
# === END HEADER ===
def _flask_method_view_collect_methods(cls: t.Type[MethodView]) -> set[str]:
    """Collects HTTP methods from base classes and directly defined methods."""
    methods = set()

    for base in cls.__bases__:
        base_methods = getattr(base, "methods", None)
        if base_methods:
            methods.update(base_methods)  # type: ignore[attr-defined]

    for key in http_method_funcs:
        if hasattr(cls, key):
            methods.add(key.upper())

    return methods


def __init_subclass__(cls, **kwargs: t.Any) -> None:
    super().__init_subclass__(**kwargs)

    if "methods" not in cls.__dict__:
        collected_methods = _flask_method_view_collect_methods(cls)

        if collected_methods:
            cls.methods = collected_methods