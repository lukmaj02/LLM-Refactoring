# === ARP Faza 4C - refactored code ===
# sample_id: flask_011
# condition: A
# timestamp: 2026-06-04T14:13:31
# original_cc: 13, original_mi: None
# changed_pct: 0.3906
# === END HEADER ===
def add_url_rule(
    self,
    rule: str,
    endpoint: str | None = None,
    view_func: ft.RouteCallable | None = None,
    provide_automatic_options: bool | None = None,
    **options: t.Any,
) -> None:
    endpoint = self._determine_endpoint(endpoint, view_func)
    options["endpoint"] = endpoint
    methods = self._determine_methods(view_func, options.pop("methods", None))
    provide_automatic_options, required_methods = self._determine_automatic_options(
        view_func, provide_automatic_options, methods
    )
    methods |= required_methods

    rule_obj = self.url_rule_class(rule, methods=methods, **options)
    rule_obj.provide_automatic_options = provide_automatic_options  # type: ignore[attr-defined]

    self.url_map.add(rule_obj)
    self._register_view_func(endpoint, view_func)


def _determine_endpoint(self, endpoint, view_func):
    if endpoint is None:
        return _endpoint_from_view_func(view_func)  # type: ignore
    return endpoint


def _determine_methods(self, view_func, methods):
    if methods is None:
        methods = getattr(view_func, "methods", None) or ("GET",)
    if isinstance(methods, str):
        raise TypeError(
            "Allowed methods must be a list of strings, for"
            ' example: @app.route(..., methods=["POST"])'
        )
    return {item.upper() for item in methods}


def _determine_automatic_options(self, view_func, provide_automatic_options, methods):
    required_methods = set(getattr(view_func, "required_methods", ()))
    if provide_automatic_options is None:
        provide_automatic_options = getattr(
            view_func, "provide_automatic_options", None
        )
    if provide_automatic_options is None:
        if "OPTIONS" not in methods and self.config["PROVIDE_AUTOMATIC_OPTIONS"]:
            provide_automatic_options = True
            required_methods.add("OPTIONS")
        else:
            provide_automatic_options = False
    return provide_automatic_options, required_methods


def _register_view_func(self, endpoint, view_func):
    if view_func is not None:
        old_func = self.view_functions.get(endpoint)
        if old_func is not None and old_func != view_func:
            raise AssertionError(
                "View function mapping is overwriting an existing"
                f" endpoint function: {endpoint}"
            )
        self.view_functions[endpoint] = view_func