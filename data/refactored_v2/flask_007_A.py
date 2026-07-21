# === ARP Faza 4C - refactored code ===
# sample_id: flask_007
# condition: A
# timestamp: 2026-06-04T14:11:56
# original_cc: 12, original_mi: None
# changed_pct: 0.4219
# === END HEADER ===
def find_best_app(module: ModuleType) -> Flask:
    """Given a module instance this tries to find the best possible
    application in the module or raises an exception.
    """
    from . import Flask

    app = _find_app_by_common_names(module, Flask)
    if app:
        return app

    app = _find_single_flask_instance(module, Flask)
    if app:
        return app

    app = _find_app_by_factory(module, Flask)
    if app:
        return app

    raise NoAppException(
        "Failed to find Flask application or factory in module"
        f" '{module.__name__}'. Use '{module.__name__}:name'"
        " to specify one."
    )


def _find_app_by_common_names(module: ModuleType, Flask) -> Flask | None:
    for attr_name in ("app", "application"):
        app = getattr(module, attr_name, None)
        if isinstance(app, Flask):
            return app
    return None


def _find_single_flask_instance(module: ModuleType, Flask) -> Flask | None:
    matches = [v for v in module.__dict__.values() if isinstance(v, Flask)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise NoAppException(
            "Detected multiple Flask applications in module"
            f" '{module.__name__}'. Use '{module.__name__}:name'"
            " to specify the correct one."
        )
    return None


def _find_app_by_factory(module: ModuleType, Flask) -> Flask | None:
    for attr_name in ("create_app", "make_app"):
        app_factory = getattr(module, attr_name, None)
        if inspect.isfunction(app_factory):
            try:
                app = app_factory()
                if isinstance(app, Flask):
                    return app
            except TypeError as e:
                if not _called_with_wrong_args(app_factory):
                    raise
                raise NoAppException(
                    f"Detected factory '{attr_name}' in module '{module.__name__}',"
                    " but could not call it without arguments. Use"
                    f" '{module.__name__}:{attr_name}(args)'"
                    " to specify arguments."
                ) from e
    return None