# === ARP Faza 4C - refactored code ===
# sample_id: httpie_028
# condition: A
# timestamp: 2026-06-04T14:08:39
# original_cc: 5, original_mi: None
# changed_pct: 0.4348
# === END HEADER ===
def is_http_command(args: List[Union[str, bytes]], env: Environment) -> bool:
    """Check whether http/https parser can parse the arguments."""

    from httpie.cli.definition import parser as http_parser
    from httpie.manager.cli import COMMANDS

    if is_top_level_command(args, COMMANDS):
        return False

    return can_parse_http_args(args, env, http_parser)


def is_top_level_command(args: List[Union[str, bytes]], commands) -> bool:
    return len(args) >= 1 and args[0] in commands


def can_parse_http_args(args: List[Union[str, bytes]], env: Environment, http_parser) -> bool:
    with env.as_silent():
        try:
            http_parser.parse_args(env=env, args=args)
            return True
        except (Exception, SystemExit):
            return False