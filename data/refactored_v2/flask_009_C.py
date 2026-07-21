# === ARP Faza 4C - refactored code ===
# sample_id: flask_009
# condition: C
# timestamp: 2026-06-04T14:13:09
# original_cc: 13, original_mi: None
# changed_pct: 0.6986
# === END HEADER ===
def _get_src_info(srcobj):
    if isinstance(srcobj, App):
        return f"application {srcobj.import_name!r}"
    if isinstance(srcobj, Blueprint):
        return f"blueprint {srcobj.name!r} ({srcobj.import_name})"
    return repr(srcobj)


def _get_triple_detail(triple):
    if triple is None:
        return "no match", 0
    return f"found ({triple[1] or '<string>'!r})", 1


def _get_current_blueprint():
    if request_ctx and request_ctx.request.blueprint is not None:
        return request_ctx.request.blueprint
    return None


def _build_attempt_info(idx, loader, srcobj, triple):
    lines = [f"{idx + 1:5}: trying loader of {_get_src_info(srcobj)}"]
    lines.extend(f"       {line}" for line in _dump_loader_info(loader))
    detail, found = _get_triple_detail(triple)
    lines.append(f"       -> {detail}")
    return lines, found


def _build_summary_info(total_found, blueprint):
    info = []
    seems_fishy = False

    if total_found == 0:
        info.append("Error: the template could not be found.")
        seems_fishy = True
    elif total_found > 1:
        info.append("Warning: multiple loaders returned a match for the template.")
        seems_fishy = True

    if blueprint is not None and seems_fishy:
        info.append(
            "  The template was looked up from an endpoint that belongs"
            f" to the blueprint {blueprint!r}."
        )
        info.append("  Maybe you did not place a template in the right folder?")
        info.append("  See https://flask.palletsprojects.com/blueprints/#templates")

    return info


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
    blueprint = _get_current_blueprint()

    for idx, (loader, srcobj, triple) in enumerate(attempts):
        attempt_lines, found = _build_attempt_info(idx, loader, srcobj, triple)
        info.extend(attempt_lines)
        total_found += found

    info.extend(_build_summary_info(total_found, blueprint))
    app.logger.info("\n".join(info))