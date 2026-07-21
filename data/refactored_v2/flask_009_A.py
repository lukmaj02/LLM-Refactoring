# === ARP Faza 4C - refactored code ===
# sample_id: flask_009
# condition: A
# timestamp: 2026-06-04T14:12:57
# original_cc: 13, original_mi: None
# changed_pct: 0.5616
# === END HEADER ===
def explain_template_loading_attempts(
    app: App,
    template: str,
    attempts: list[
        tuple[
            BaseLoader,
            Scaffold,
            tuple[str, str | None, t.Callable[[], bool] | None] | None,
        ]
    ],
) -> None:
    """This should help developers understand what failed"""
    info = [f"Locating template {template!r}:"]
    total_found = 0
    blueprint = _get_blueprint()

    for idx, (loader, srcobj, triple) in enumerate(attempts):
        src_info = _get_source_info(srcobj)
        info.append(f"{idx + 1:5}: trying loader of {src_info}")

        for line in _dump_loader_info(loader):
            info.append(f"       {line}")

        detail, found = _get_detail_and_found(triple)
        total_found += found
        info.append(f"       -> {detail}")

    seems_fishy = _log_fishy_info(info, total_found)

    if blueprint is not None and seems_fishy:
        _log_blueprint_info(info, blueprint)

    app.logger.info("\n".join(info))


def _get_blueprint():
    if request_ctx and request_ctx.request.blueprint is not None:
        return request_ctx.request.blueprint
    return None


def _get_source_info(srcobj):
    if isinstance(srcobj, App):
        return f"application {srcobj.import_name!r}"
    elif isinstance(srcobj, Blueprint):
        return f"blueprint {srcobj.name!r} ({srcobj.import_name})"
    return repr(srcobj)


def _get_detail_and_found(triple):
    if triple is None:
        return "no match", 0
    return f"found ({triple[1] or '<string>'!r})", 1


def _log_fishy_info(info, total_found):
    seems_fishy = False
    if total_found == 0:
        info.append("Error: the template could not be found.")
        seems_fishy = True
    elif total_found > 1:
        info.append("Warning: multiple loaders returned a match for the template.")
        seems_fishy = True
    return seems_fishy


def _log_blueprint_info(info, blueprint):
    info.append(
        "  The template was looked up from an endpoint that belongs"
        f" to the blueprint {blueprint!r}."
    )
    info.append("  Maybe you did not place a template in the right folder?")
    info.append("  See https://flask.palletsprojects.com/blueprints/#templates")