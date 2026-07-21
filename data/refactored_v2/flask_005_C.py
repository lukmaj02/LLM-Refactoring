# === ARP Faza 4C - refactored code ===
# sample_id: flask_005
# condition: C
# timestamp: 2026-06-04T14:12:07
# original_cc: 14, original_mi: None
# changed_pct: 0.4430
# === END HEADER ===
def _parse_app_name_expr(app_name: str):
    """Parse app_name into (name, args, kwargs). Raises NoAppException on failure."""
    try:
        expr = ast.parse(app_name.strip(), mode="eval").body
    except SyntaxError:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        ) from None

    if isinstance(expr, ast.Name):
        return expr.id, [], {}

    if isinstance(expr, ast.Call):
        if not isinstance(expr.func, ast.Name):
            raise NoAppException(
                f"Function reference must be a simple name: {app_name!r}."
            )

        try:
            args = [ast.literal_eval(arg) for arg in expr.args]
            kwargs = {
                kw.arg: ast.literal_eval(kw.value)
                for kw in expr.keywords
                if kw.arg is not None
            }
        except ValueError:
            raise NoAppException(
                f"Failed to parse arguments as literal values: {app_name!r}."
            ) from None

        return expr.func.id, args, kwargs

    raise NoAppException(
        f"Failed to parse {app_name!r} as an attribute name or function call."
    )


def _call_app_factory(attr, args, kwargs, app_name, module_name):
    """Call the factory function and return the result, raising NoAppException on failure."""
    try:
        return attr(*args, **kwargs)
    except TypeError as e:
        if not _called_with_wrong_args(attr):
            raise

        raise NoAppException(
            f"The factory {app_name!r} in module"
            f" {module_name!r} could not be called with the"
            " specified arguments."
        ) from e


def find_app_by_string(module: ModuleType, app_name: str) -> Flask:
    """Check if the given string is a variable name or a function. Call
    a function to get the app instance, or return the variable directly.
    """
    from . import Flask

    name, args, kwargs = _parse_app_name_expr(app_name)

    try:
        attr = getattr(module, name)
    except AttributeError as e:
        raise NoAppException(
            f"Failed to find attribute {name!r} in {module.__name__!r}."
        ) from e

    if inspect.isfunction(attr):
        app = _call_app_factory(attr, args, kwargs, app_name, module.__name__)
    else:
        app = attr

    if isinstance(app, Flask):
        return app

    raise NoAppException(
        "A valid Flask application was not obtained from"
        f" '{module.__name__}:{app_name}'."
    )