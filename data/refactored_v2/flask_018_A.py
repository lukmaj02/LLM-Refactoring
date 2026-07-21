# === ARP Faza 4C - refactored code ===
# sample_id: flask_018
# condition: A
# timestamp: 2026-06-04T14:15:06
# original_cc: 7, original_mi: None
# changed_pct: 0.7391
# === END HEADER ===
def __init_subclass__(cls, **kwargs: t.Any) -> None:
    super().__init_subclass__(**kwargs)

    if "methods" in cls.__dict__:
        return

    methods = cls._collect_methods_from_bases()
    methods.update(cls._collect_methods_from_http_funcs())

    if methods:
        cls.methods = methods

@classmethod
def _collect_methods_from_bases(cls) -> set:
    methods = set()
    for base in cls.__bases__:
        if getattr(base, "methods", None):
            methods.update(base.methods)  # type: ignore[attr-defined]
    return methods

@classmethod
def _collect_methods_from_http_funcs(cls) -> set:
    return {key.upper() for key in http_method_funcs if hasattr(cls, key)}