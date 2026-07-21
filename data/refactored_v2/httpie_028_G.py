# === ARP Faza 4C - refactored code ===
# sample_id: httpie_028
# condition: G
# timestamp: 2026-06-04T14:08:33
# original_cc: 5, original_mi: None
# changed_pct: 0.5909
# === END HEADER ===
def _can_parse_with_http_parser(args: List[Union[str, bytes]], env: Environment) -> bool:
    """Helper to check if http_parser can parse the arguments."""
    from httpie.cli.definition import parser as http_parser
    with env.as_silent():
        try:
            http_parser.parse_args(env=env, args=args)
            return True
        except (Exception, SystemExit):
            return False


def is_http_command(args: List[Union[str, bytes]], env: Environment) -> bool:
    """Check whether http/https parser can parse the arguments."""

    from httpie.manager.cli import COMMANDS

    # If the user already selected a top-level sub-command, never
    # show the http/https version. E.g httpie plugins pie.dev/post
    if args and args[0] in COMMANDS:
        return False

    return _can_parse_with_http_parser(args, env)