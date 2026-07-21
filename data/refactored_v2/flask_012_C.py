# === ARP Faza 4C - refactored code ===
# sample_id: flask_012
# condition: C
# timestamp: 2026-06-04T14:14:09
# original_cc: 23, original_mi: None
# changed_pct: 0.3784
# === END HEADER ===
def _resolve_bp_subdomain(state, bp_options, blueprint):
    bp_subdomain = bp_options.get("subdomain")
    if bp_subdomain is None:
        bp_subdomain = blueprint.subdomain

    if state.subdomain is not None and bp_subdomain is not None:
        bp_options["subdomain"] = bp_subdomain + "." + state.subdomain
    elif bp_subdomain is not None:
        bp_options["subdomain"] = bp_subdomain
    elif state.subdomain is not None:
        bp_options["subdomain"] = state.subdomain


def _resolve_bp_url_prefix(state, bp_options, blueprint):
    bp_url_prefix = bp_options.get("url_prefix")
    if bp_url_prefix is None:
        bp_url_prefix = blueprint.url_prefix

    if state.url_prefix is not None and bp_url_prefix is not None:
        bp_options["url_prefix"] = (
            state.url_prefix.rstrip("/") + "/" + bp_url_prefix.lstrip("/")
        )
    elif bp_url_prefix is not None:
        bp_options["url_prefix"] = bp_url_prefix
    elif state.url_prefix is not None:
        bp_options["url_prefix"] = state.url_prefix


def _register_cli_commands(self, app, name, cli_resolved_group):
    if not self.cli.commands:
        return

    if cli_resolved_group is None:
        app.cli.commands.update(self.cli.commands)
    else:
        self.cli.name = name if cli_resolved_group is _sentinel else cli_resolved_group
        app.cli.add_command(self.cli)


def register(self, app: App, options: dict[str, t.Any]) -> None:
    """Called by :meth:`Flask.register_blueprint` to register all
    views and callbacks registered on the blueprint with the
    application. Creates a :class:`.BlueprintSetupState` and calls
    each :meth:`record` callback with it.

    :param app: The application this blueprint is being registered
        with.
    :param options: Keyword arguments forwarded from
        :meth:`~Flask.register_blueprint`.

    .. versionchanged:: 2.3
        Nested blueprints now correctly apply subdomains.

    .. versionchanged:: 2.1
        Registering the same blueprint with the same name multiple
        times is an error.

    .. versionchanged:: 2.0.1
        Nested blueprints are registered with their dotted name.
        This allows different blueprints with the same name to be
        nested at different locations.

    .. versionchanged:: 2.0.1
        The ``name`` option can be used to change the (pre-dotted)
        name the blueprint is registered with. This allows the same
        blueprint to be registered multiple times with unique names
        for ``url_for``.
    """
    name_prefix = options.get("name_prefix", "")
    self_name = options.get("name", self.name)
    name = f"{name_prefix}.{self_name}".lstrip(".")

    if name in app.blueprints:
        bp_desc = "this" if app.blueprints[name] is self else "a different"
        existing_at = f" '{name}'" if self_name != name else ""

        raise ValueError(
            f"The name '{self_name}' is already registered for"
            f" {bp_desc} blueprint{existing_at}. Use 'name=' to"
            f" provide a unique name."
        )

    first_bp_registration = not any(bp is self for bp in app.blueprints.values())
    first_name_registration = name not in app.blueprints

    app.blueprints[name] = self
    self._got_registered_once = True
    state = self.make_setup_state(app, options, first_bp_registration)

    if self.has_static_folder:
        state.add_url_rule(
            f"{self.static_url_path}/<path:filename>",
            view_func=self.send_static_file,  # type: ignore[attr-defined]
            endpoint="static",
        )

    if first_bp_registration or first_name_registration:
        self._merge_blueprint_funcs(app, name)

    for deferred in self.deferred_functions:
        deferred(state)

    cli_resolved_group = options.get("cli_group", self.cli_group)
    _register_cli_commands(self, app, name, cli_resolved_group)

    for blueprint, bp_options in self._blueprints:
        bp_options = bp_options.copy()
        _resolve_bp_subdomain(state, bp_options, blueprint)
        _resolve_bp_url_prefix(state, bp_options, blueprint)
        bp_options["name_prefix"] = name
        blueprint.register(app, bp_options)