# === ARP Faza 4C - refactored code ===
# sample_id: flask_002
# condition: G
# timestamp: 2026-06-04T14:11:57
# original_cc: 12, original_mi: None
# changed_pct: 0.9262
# === END HEADER ===
def _check_cli_run_and_exit_if_needed() -> bool:
    """Check if the app is being run from the Flask CLI and exit if so,
    displaying a warning if not in a reloader process.
    """
    if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
        if not is_running_from_reloader():
            click.secho(
                " * Ignoring a call to 'app.run()' that would block"
                " the current 'flask' CLI command.\n"
                "   Only call 'app.run()' in an 'if __name__ =="
                ' "__main__"\' guard.',
                fg="red",