# === ARP Faza 4C - refactored code ===
# sample_id: flask_002
# condition: A
# timestamp: 2026-06-04T14:10:24
# original_cc: 12, original_mi: None
# changed_pct: 0.7623
# === END HEADER ===
def run(
    self,
    host: str | None = None,
    port: int | None = None,
    debug: bool | None = None,
    load_dotenv: bool = True,
    **options: t.Any,
) -> None:
    if os.environ.get("FLASK_RUN_FROM_CLI") == "true":
        self._handle_cli_run()
        return

    if get_load_dotenv(load_dotenv):
        self._load_dotenv()

    if debug is not None:
        self.debug = bool(debug)

    host, port = self._determine_host_port(host, port)

    options.setdefault("use_reloader", self.debug)
    options.setdefault("use_debugger", self.debug)
    options.setdefault("threaded", True)

    cli.show_server_banner(self.debug, self.name)

    from werkzeug.serving import run_simple

    try:
        run_simple(t.cast(str, host), port, self, **options)
    finally:
        self._got_first_request = False


def _handle_cli_run(self):
    if not is_running_from_reloader():
        click.secho(
            " * Ignoring a call to 'app.run()' that would block"
            " the current 'flask' CLI command.\n"
            "   Only call 'app.run()' in an 'if __name__ =="
            ' "__main__"\' guard.',
            fg="red",
        )


def _load_dotenv(self):
    cli.load_dotenv()
    if "FLASK_DEBUG" in os.environ:
        self.debug = get_debug_flag()


def _determine_host_port(self, host, port):
    server_name = self.config.get("SERVER_NAME")
    sn_host, sn_port = (None, None)

    if server_name:
        sn_host, _, sn_port = server_name.partition(":")

    if not host:
        host = sn_host or "127.0.0.1"

    if port or port == 0:
        port = int(port)
    elif sn_port:
        port = int(sn_port)
    else:
        port = 5000

    return host, port