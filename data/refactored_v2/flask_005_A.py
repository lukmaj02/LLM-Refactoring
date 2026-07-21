# === ARP Faza 4C - refactored code ===
# sample_id: flask_005
# condition: A
# timestamp: 2026-06-04T14:11:14
# original_cc: 14, original_mi: None
# changed_pct: 0.3750
# === END HEADER ===
def find_app_by_string(module: ModuleType, app_name: str) -> Flask:
    """Check if the given string is a variable name or a function. Call
    a function to get the app instance, or return the variable directly.
    """
    from . import Flask

    expr = _parse_app_name(app_name)

    name, args, kwargs = _extract_name_args_kwargs(expr, app_name)

    attr = _get_module_attribute(module, name)

    app = _get_app_from_attribute(attr, args, kwargs, app_name, module)

    if isinstance(app, Flask):
        return app

    raise NoAppException(
        "A valid Flask application was not obtained from"
        f" '{module.__name__}:{app_name}'."
    )


def _parse_app_name(app_name: str):
    try:
        return ast.parse(app_name.strip(), mode="eval").body
    except SyntaxError:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        ) from None


def _extract_name_args_kwargs(expr, app_name: str):
    if isinstance(expr, ast.Name):
        return expr.id, [], {}
    elif isinstance(expr, ast.Call):
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
            return expr.func.id, args, kwargs
        except ValueError:
            raise NoAppException(
                f"Failed to parse arguments as literal values: {app_name!r}."
            ) from None
    else:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )


def _get_module_attribute(module: ModuleType, name: str):
    try:
        return getattr(module, name)
    except AttributeError as e:
        raise NoAppException(
            f"Failed to find attribute {name!r} in {module.__name__!r}."
        ) from e


def _get_app_from_attribute(attr, args, kwargs, app_name: str, module: ModuleType):
    if inspect.isfunction(attr):
        try:
            return attr(*args, **kwargs)
        except TypeError as e:
            if not _called_with_wrong_args(attr):
                raise
            raise NoAppException(
                f"The factory {app_name!r} in module"
                f" {module.__name__!r} could not be called with the"
                " specified arguments."
            ) from e
    return attr