# === ARP Faza 4C - refactored code ===
# sample_id: flask_009
# condition: G
# timestamp: 2026-06-04T14:15:15
# original_cc: 13, original_mi: None
# changed_pct: 0.7284
# === END HEADER ===
def _get_source_object_info(srcobj: Scaffold) -> str:
    if isinstance(srcobj, App):
        return f"application {srcobj.import_name!r}"
    elif isinstance(srcobj, Blueprint):
        return f"blueprint {srcobj.name!r} ({srcobj.import_name})"
    else:
        return repr(srcobj)


def _format_single_attempt_info(
    idx: int,
    loader: BaseLoader,
    srcobj: Scaffold,
    triple: tuple[str, str | None, t.Callable[[], bool] | None] | None,
) -> tuple[list[str], bool]:
    lines = []
    src_info = _get_source_object_info(srcobj)
    lines.append(f"{idx + 1:5}: trying loader of {src_info}")

    for line in _dump_loader_info(loader):
        lines.append(f"       {line}")

    is_found = False
    if triple is None:
        detail = "no match"
    else:
        detail = f"found ({triple[1] or '<string>'!r})"
        is_found = True
    lines.append(f"       -> {detail}")
    return lines, is_found


def _append_summary_and_suggestions(
    info: list[str], total_found: int, blueprint: Blueprint | None
) -> None:
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
    blueprint = None
    if request_ctx and request_ctx.request.blueprint is not None:
        blueprint = request_ctx.request.blueprint

    for idx, (loader, srcobj, triple) in enumerate(attempts):
        attempt_lines, is_found = _format_single_attempt_info(
            idx, loader, srcobj, triple
        )
        info.extend(attempt_lines)
        if is_found:
            total_found += 1

    _append_summary_and_suggestions(info, total_found, blueprint)

    app.logger.info("\n".join(info))