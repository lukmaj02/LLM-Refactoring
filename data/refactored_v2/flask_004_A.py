# === ARP Faza 4C - refactored code ===
# sample_id: flask_004
# condition: A
# timestamp: 2026-06-04T14:10:54
# original_cc: 18, original_mi: None
# changed_pct: 0.3729
# === END HEADER ===
def routes_command(sort: str, all_methods: bool) -> None:
    """Show all registered routes with endpoints and methods."""
    rules = list(current_app.url_map.iter_rules())

    if not rules:
        click.echo("No routes were registered.")
        return

    ignored_methods = set() if all_methods else {"HEAD", "OPTIONS"}
    host_matching = current_app.url_map.host_matching
    has_domain = any(rule.host if host_matching else rule.subdomain for rule in rules)
    rows = [_get_route_row(rule, ignored_methods, host_matching, has_domain) for rule in rules]

    headers, sorts = _get_headers_and_sorts(has_domain)
    _sort_rows(rows, sort, sorts)
    _print_routes(rows, headers)


def _get_route_row(rule, ignored_methods, host_matching, has_domain):
    row = [
        rule.endpoint,
        ", ".join(sorted((rule.methods or set()) - ignored_methods)),
    ]

    if has_domain:
        row.append((rule.host if host_matching else rule.subdomain) or "")

    row.append(rule.rule)
    return row


def _get_headers_and_sorts(has_domain):
    headers = ["Endpoint", "Methods"]
    sorts = ["endpoint", "methods"]

    if has_domain:
        headers.append("Host" if host_matching else "Subdomain")
        sorts.append("domain")

    headers.append("Rule")
    sorts.append("rule")
    return headers, sorts


def _sort_rows(rows, sort, sorts):
    try:
        rows.sort(key=itemgetter(sorts.index(sort)))
    except ValueError:
        pass


def _print_routes(rows, headers):
    rows.insert(0, headers)
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    rows.insert(1, ["-" * w for w in widths])
    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))

    for row in rows:
        click.echo(template.format(*row))