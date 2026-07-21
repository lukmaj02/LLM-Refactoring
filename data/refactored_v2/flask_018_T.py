# === ARP Faza 4C - refactored code ===
# sample_id: flask_018
# condition: T
# timestamp: 2026-06-04T14:10:48
# original_cc: 7, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __init_subclass__(cls, **kwargs: t.Any) -> None:
    super().__init_subclass__(**kwargs)

    if "methods" not in cls.__dict__:
        methods = set()

        for base in cls.__bases__:
            if getattr(base, "methods", None):
                methods.update(base.methods)  # type: ignore[attr-defined]

        for key in http_method_funcs:
            if hasattr(cls, key):
                methods.add(key.upper())

        if methods:
            cls.methods = methods
