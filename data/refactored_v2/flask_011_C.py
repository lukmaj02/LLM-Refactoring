# === ARP Faza 4C - refactored code ===
# sample_id: flask_011
# condition: C
# timestamp: 2026-06-04T14:13:45
# original_cc: 13, original_mi: None
# changed_pct: 0.7246
# === END HEADER ===
def _resolve_methods(view_func, options):
    methods = options.pop("methods", None)

    if methods is None:
        methods = getattr(view_func, "methods", None) or ("GET",)

    if isinstance(methods, str):
        raise TypeError(
            "Allowed methods must be a list of strings, for"
            ' example: @app.route(..., methods=["POST"])'
        )

    return {item.upper() for item in methods}


def _resolve_provide_automatic_options(view_func, methods, provide_automatic_options, required_methods, config):
    if provide_automatic_options is None:
        provide_automatic_options = getattr(
            view_func, "provide_automatic_options", None
        )

    if provide_automatic_options is None:
        if "OPTIONS" not in methods and config["PROVIDE_AUTOMATIC_OPTIONS"]:
            provide_automatic_options = True
            required_methods.add("OPTIONS")
        else:
            provide_automatic_options = False

    return provide_automatic_options


def _register_view_func(view_functions, endpoint, view_func):
    if view_func is None:
        return

    old_func = view_functions.get(endpoint)
    if old_func is not None and old_func != view_func:
        raise AssertionError(
            "View function mapping is overwriting an existing"
            f" endpoint function: {endpoint}"
        )
    view_functions[endpoint] = view_func


@setupmethod
def add_url_rule(
    self,
    rule: str,
    endpoint: str | None = None,
    view_func: ft.RouteCallable | None = None,
    provide_automatic_options: bool | None = None,
    **options: t.Any,
) -> None:
    if endpoint is None:
        endpoint = _endpoint_from_view_func(view_func)  # type: ignore
    options["endpoint"] = endpoint

    methods = _resolve_methods(view_func, options)
    required_methods: set[str] = set(getattr(view_func, "required_methods", ()))
    provide_automatic_options = _resolve_provide_automatic_options(
        view_func, methods, provide_automatic_options, required_methods, self.config
    )
    methods |= required_methods

    rule_obj = self.url_rule_class(rule, methods=methods, **options)
    rule_obj.provide_automatic_options = provide_automatic_options  # type: ignore[attr-defined]

    self.url_map.add(rule_obj)
    _register_view_func(self.view_functions, endpoint, view_func)