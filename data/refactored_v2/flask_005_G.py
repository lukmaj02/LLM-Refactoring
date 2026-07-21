# === ARP Faza 4C - refactored code ===
# sample_id: flask_005
# condition: G
# timestamp: 2026-06-04T14:13:33
# original_cc: 14, original_mi: None
# changed_pct: 0.4000
# === END HEADER ===
def _parse_app_name_expression(
    app_name: str,
) -> tuple[str, list[t.Any], dict[str, t.Any]]:
    """Parse the app_name string into an AST expression and extract the
    attribute name, arguments, and keyword arguments.
    """
    try:
        expr = ast.parse(app_name.strip(), mode="eval").body
    except SyntaxError:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        ) from None

    if isinstance(expr, ast.Name):
        return expr.id, [], {}
    elif isinstance(expr, ast.Call):
        if not isinstance(expr.func, ast.Name):
            raise NoAppException(
                f"Function reference must be a simple name: {app_name!r}."
            )

        name = expr.func.id

        try:
            args = [ast.literal_eval(arg) for arg in expr.args]
            kwargs = {
                kw.arg: ast.literal_eval(kw.value)
                for kw in expr.keywords
                if kw.arg is not None
            }
            return name, args, kwargs
        except ValueError:
            raise NoAppException(
                f"Failed to parse arguments as literal values: {app_name!r}."
            ) from None
    else:
        raise NoAppException(
            f"Failed to parse {app_name!r} as an attribute name or function call."
        )


def _get_module_attribute(module: ModuleType, name: str) -> t.Any:
    """Retrieve an attribute from a module, raising NoAppException if not found."""
    try:
        return getattr(module, name)
    except AttributeError as e:
        raise NoAppException(
            f"Failed to find attribute {name!r} in {module.__name__!r}."
        ) from e


def _call_app_factory(
    module: ModuleType, app_name: str, attr: t.Any, args: list[t.Any], kwargs: dict[str, t.Any]
) -> t.Any:
    """If the attribute is a function, call it with the given arguments.
    Handle TypeError if arguments are incorrect.
    """
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


def _validate_flask_app(
    module: ModuleType, app_name: str, app: t.Any, Flask_cls: t.Type[Flask]
) -> Flask:
    """Validate that the given object is a Flask application instance."""
    if isinstance(app, Flask_cls):
        return app

    raise NoAppException(
        "A valid Flask application was not obtained from"
        f" '{module.__name__}:{app_name}'."
    )


def find_app_by_string(module: ModuleType, app_name: str) -> Flask:
    """Check if the given string is a variable name or a function. Call
    a function to get the app instance, or return the variable directly.
    """
    from . import Flask

    name, args, kwargs = _parse_app_name_expression(app_name)
    attr = _get_module_attribute(module, name)
    app = _call_app_factory(module, app_name, attr, args, kwargs)
    return _validate_flask_app(module, app_name, app, Flask)