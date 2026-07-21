# === ARP Faza 4C - refactored code ===
# sample_id: httpie_028
# condition: C
# timestamp: 2026-06-04T14:08:31
# original_cc: 5, original_mi: None
# changed_pct: 0.1667
# === END HEADER ===
def is_http_command(args: List[Union[str, bytes]], env: Environment) -> bool:
    """Check whether http/https parser can parse the arguments."""

    from httpie.cli.definition import parser as http_parser
    from httpie.manager.cli import COMMANDS

    # If the user already selected a top-level sub-command, never
    # show the http/https version. E.g httpie plugins pie.dev/post
    if args and args[0] in COMMANDS:
        return False

    with env.as_silent():
        try:
            http_parser.parse_args(env=env, args=args)
            return True
        except (Exception, SystemExit):
            return False