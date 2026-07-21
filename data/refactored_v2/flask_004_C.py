# === ARP Faza 4C - refactored code ===
# sample_id: flask_004
# condition: C
# timestamp: 2026-06-04T14:11:46
# original_cc: 18, original_mi: None
# changed_pct: 0.6842
# === END HEADER ===
def _get_domain_value(rule, host_matching):
    return (rule.host if host_matching else rule.subdomain) or ""


def _build_route_row(rule, ignored_methods, has_domain, host_matching):
    row = [
        rule.endpoint,
        ", ".join(sorted((rule.methods or set()) - ignored_methods)),
    ]
    if has_domain:
        row.append(_get_domain_value(rule, host_matching))
    row.append(rule.rule)
    return row


def _build_headers_and_sorts(has_domain, host_matching):
    headers = ["Endpoint", "Methods"]
    sorts = ["endpoint", "methods"]
    if has_domain:
        headers.append("Host" if host_matching else "Subdomain")
        sorts.append("domain")
    headers.append("Rule")
    sorts.append("rule")
    return headers, sorts


def _format_and_print_rows(rows, headers, sort):
    sorts = ["endpoint", "methods"]
    if len(headers) == 4:
        sorts.insert(2, "domain")
    sorts.append("rule")

    try:
        rows.sort(key=itemgetter(sorts.index(sort)))
    except ValueError:
        pass

    rows.insert(0, headers)
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    rows.insert(1, ["-" * w for w in widths])
    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))

    for row in rows:
        click.echo(template.format(*row))


def routes_command(sort: str, all_methods: bool) -> None:
    """Show all registered routes with endpoints and methods."""
    rules = list(current_app.url_map.iter_rules())

    if not rules:
        click.echo("No routes were registered.")
        return

    ignored_methods = set() if all_methods else {"HEAD", "OPTIONS"}
    host_matching = current_app.url_map.host_matching
    has_domain = any(rule.host if host_matching else rule.subdomain for rule in rules)

    rows = [
        _build_route_row(rule, ignored_methods, has_domain, host_matching)
        for rule in rules
    ]
    headers, sorts = _build_headers_and_sorts(has_domain, host_matching)

    try:
        rows.sort(key=itemgetter(sorts.index(sort)))
    except ValueError:
        pass

    rows.insert(0, headers)
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    rows.insert(1, ["-" * w for w in widths])
    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))

    for row in rows:
        click.echo(template.format(*row))