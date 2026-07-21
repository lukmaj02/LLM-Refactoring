# === ARP Faza 4C - refactored code ===
# sample_id: flask_023
# condition: G
# timestamp: 2026-06-04T14:20:09
# original_cc: 5, original_mi: None
# changed_pct: 0.2857
# === END HEADER ===
def show_server_banner(debug: bool, app_import_path: str | None) -> None:
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if is_running_from_reloader():
        return

    if app_import_path is not None:
        click.echo(f" * Serving Flask app '{app_import_path}'")

    # The 'debug' parameter is typed as 'bool' and is always a boolean value
    # when called from 'run_command' (via 'get_debug_flag()').
    # Therefore, 'debug is not None' is always true and the check is redundant.
    click.echo(f" * Debug mode: {'on' if debug else 'off'}")