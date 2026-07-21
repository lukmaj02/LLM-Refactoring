# === ARP Faza 4C - refactored code ===
# sample_id: httpie_001
# condition: G
# timestamp: 2026-06-04T13:56:35
# original_cc: 21, original_mi: None
# changed_pct: 0.9286
# === END HEADER ===
def _get_httpie_session_and_headers(
    env: Environment, args: argparse.Namespace
) -> tuple[Any, Optional[HTTPHeadersDict]]:
    """Initializes HTTPie session if args.session or args.session_read_only is set."""
    httpie_session = None
    httpie_session_headers = None
    if args.session or args.session_read_only:
        session_name = args.session or args.session_read_only
        httpie_session = get_httpie_session(
            env=env,
            config_dir=env.config.directory,
            session_name=session_name,
            host=args.headers.get('Host'),