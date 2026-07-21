# === ARP Faza 4C - refactored code ===
# sample_id: flask_004
# condition: G
# timestamp: 2026-06-04T14:13:00
# original_cc: 18, original_mi: None
# changed_pct: 0.8333
# === END HEADER ===
def _get_route_data(
    rule, ignored_methods: set[str], host_matching: bool, has_domain: bool
) -> list[str]:
    methods_str = ", ".join(sorted((rule.methods or set()) - ignored_methods))
    row = [rule.endpoint, methods_str]

    if has_domain:
        domain_value = (rule.host if host_matching else rule.subdomain) or ""
        row.append(domain_value)

    row.append(rule.rule)
    return row


def _prepare_table_headers(
    host_matching: bool, has_domain: bool
) -> tuple[list[str], list[str]]:
    headers = ["Endpoint", "Methods"]
    sorts = ["endpoint", "methods"]

    if has_domain:
        headers.append("Host" if host_matching else "Subdomain")
        sorts.append("domain")

    headers.append("Rule")
    sorts.append("rule")
    return headers, sorts


def _print_table(
    rows: list[list[str]], headers: list[str], sorts: list[str], sort_key: str
) -> None:
    try:
        rows.sort(key=itemgetter(sorts.index(sort_key)))
    except ValueError:
        pass

    rows.insert(0, headers)
    widths = [max(len(row[i]) for row in rows) for i in range(len(headers))]
    rows.insert(1, ["-" * w for w in widths])
    template = "  ".join(f"{{{i}:<{w}}}" for i, w in enumerate(widths))

    for row in rows:
        click.echo(template.format(*row))


@click.command("routes", short_help="Show the routes for the app.")
@click.option(
    "--sort",
    "-s",
    type=click.Choice(("endpoint", "methods", "domain", "rule", "match")),
    default="endpoint",
    help=(
        "Method to sort routes by. 'match' is the order that Flask will match routes"
        " when dispatching a request."
    ),
)
@click.option("--all-methods", is_flag=True, help="Show HEAD and OPTIONS methods.")
@with_appcontext
def routes_command(sort: str, all_methods: bool) -> None:
    """Show all registered routes with endpoints and methods."""
    rules = list(current_app.url_map.iter_rules())

    if not rules:
        click.echo("No routes were registered.")
        return

    ignored_methods = set() if all_methods else {"HEAD", "OPTIONS"}
    host_matching = current_app.url_map.host_matching
    has_domain = any(rule.host if host_matching else rule.subdomain for rule in rules)

    rows