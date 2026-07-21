# SNAPSHOT METADATA
# sample_id: flask_023
# repo: flask
# file: data/repos/flask/src/flask/cli.py
# function: show_server_banner
# cc: 5 | mi: N/A | loc: 12
# extracted: 2026-05-01T11:47:37

def show_server_banner(debug: bool, app_import_path: str | None) -> None:
    """Show extra startup messages the first time the server is run,
    ignoring the reloader.
    """
    if is_running_from_reloader():
        return

    if app_import_path is not None:
        click.echo(f" * Serving Flask app '{app_import_path}'")

    if debug is not None:
        click.echo(f" * Debug mode: {'on' if debug else 'off'}")
