# === ARP Faza 4C - refactored code ===
# sample_id: flask_023
# condition: C
# timestamp: 2026-06-04T14:16:55
# original_cc: 5, original_mi: None
# changed_pct: 0.4118
# === END HEADER ===
def show_server_banner(debug: bool, app_import_path: str | None) -> None:
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if is_running_from_reloader():
        return

    messages = []

    if app_import_path is not None:
        messages.append(f" * Serving Flask app '{app_import_path}'")

    if debug is not None:
        messages.append(f" * Debug mode: {'on' if debug else 'off'}")

    for message in messages:
        click.echo(message)