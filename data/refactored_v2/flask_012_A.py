# === ARP Faza 4C - refactored code ===
# sample_id: flask_012
# condition: A
# timestamp: 2026-06-04T14:13:46
# original_cc: 23, original_mi: None
# changed_pct: 0.6762
# === END HEADER ===
def register(self, app: App, options: dict[str, t.Any]) -> None:
    name_prefix = options.get("name_prefix", "")
    self_name = options.get("name", self.name)
    name = f"{name_prefix}.{self_name}".lstrip(".")

    self._validate_blueprint_name(app, name, self_name)

    first_bp_registration = not any(bp is self for bp in app.blueprints.values())
    first_name_registration = name not in app.blueprints

    app.blueprints[name] = self
    self._got_registered_once = True
    state = self.make_setup_state(app, options, first_bp_registration)

    if self.has_static_folder:
        self._add_static_url_rule(state)

    if first_bp_registration or first_name_registration:
        self._merge_blueprint_funcs(app, name)

    self._execute_deferred_functions(state)
    self._register_cli_commands(app, options, name)

    for blueprint, bp_options in self._blueprints:
        self._register_nested_blueprint(app, state, blueprint, bp_options, name)

def _validate_blueprint_name(self, app: App, name: str, self_name: str) -> None:
    if name in app.blueprints:
        bp_desc = "this" if app.blueprints[name] is self else "a different"
        existing_at = f" '{name}'" if self_name != name else ""
        raise ValueError(
            f"The name '{self_name}' is already registered for"
            f" {bp_desc} blueprint{existing_at}. Use 'name=' to"
            f" provide a unique name."
        )

def _add_static_url_rule(self, state: BlueprintSetupState) -> None:
    state.add_url_rule(
        f"{self.static_url_path}/<path:filename>",
        view_func=self.send_static_file,  # type: ignore[attr-defined]
        endpoint="static",
    )

def _execute_deferred_functions(self, state: BlueprintSetupState) -> None:
    for deferred in self.deferred_functions:
        deferred(state)

def _register_cli_commands(self, app: App, options: dict[str, t.Any], name: str) -> None:
    cli_resolved_group = options.get("cli_group", self.cli_group)
    if self.cli.commands:
        if cli_resolved_group is None:
            app.cli.commands.update(self.cli.commands)
        elif cli_resolved_group is _sentinel:
            self.cli.name = name
            app.cli.add_command(self.cli)
        else:
            self.cli.name = cli_resolved_group
            app.cli.add_command(self.cli)

def _register_nested_blueprint(
    self, app: App, state: BlueprintSetupState, blueprint: Blueprint, bp_options: dict[str, t.Any], name: str
) -> None:
    bp_options = bp_options.copy()
    bp_options["subdomain"] = self._resolve_subdomain(state, blueprint, bp_options)
    bp_options["url_prefix"] = self._resolve_url_prefix(state, blueprint, bp_options)
    bp_options["name_prefix"] = name
    blueprint.register(app, bp_options)

def _resolve_subdomain(
    self, state: BlueprintSetupState, blueprint: Blueprint, bp_options: dict[str, t.Any]
) -> str | None:
    bp_subdomain = bp_options.get("subdomain", blueprint.subdomain)
    if state.subdomain is not None and bp_subdomain is not None:
        return bp_subdomain + "." + state.subdomain
    return bp_subdomain or state.subdomain

def _resolve_url_prefix(
    self, state: BlueprintSetupState, blueprint: Blueprint, bp_options: dict[str, t.Any]
) -> str | None:
    bp_url_prefix = bp_options.get("url_prefix", blueprint.url_prefix)
    if state.url_prefix is not None and bp_url_prefix is not None:
        return state.url_prefix.rstrip("/") + "/" + bp_url_prefix.lstrip("/")
    return bp_url_prefix or state.url_prefix