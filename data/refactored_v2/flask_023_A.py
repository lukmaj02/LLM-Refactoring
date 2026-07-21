# === ARP Faza 4C - refactored code ===
# sample_id: flask_023
# condition: A
# timestamp: 2026-06-04T14:16:20
# original_cc: 5, original_mi: None
# changed_pct: 0.4286
# === END HEADER ===
def show_server_banner(debug: bool, app_import_path: str | None) -> None:
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if is_running_from_reloader():
        return

    _echo_if_not_none(app_import_path, " * Serving Flask app '{}'")
    _echo_if_not_none(debug, " * Debug mode: {}")


def _echo_if_not_none(value, message_template: str) -> None:
    if value is not None:
        click.echo(message_template.format('on' if value else 'off' if isinstance(value, bool) else value))