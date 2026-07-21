# SNAPSHOT METADATA
# sample_id: flask_018
# repo: flask
# file: data/repos/flask/src/flask/views.py
# function: MethodView.__init_subclass__
# cc: 7 | mi: N/A | loc: 16
# extracted: 2026-05-01T11:47:37

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
