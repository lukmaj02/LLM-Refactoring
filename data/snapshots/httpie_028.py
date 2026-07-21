# SNAPSHOT METADATA
# sample_id: httpie_028
# repo: httpie
# file: data/repos/httpie/httpie/manager/__main__.py
# function: is_http_command
# cc: 5 | mi: N/A | loc: 18
# extracted: 2026-05-01T11:47:36

def is_http_command(args: List[Union[str, bytes]], env: Environment) -> bool:
    """Check whether http/https parser can parse the arguments."""

    from httpie.cli.definition import parser as http_parser
    from httpie.manager.cli import COMMANDS

    # If the user already selected a top-level sub-command, never
    # show the http/https version. E.g httpie plugins pie.dev/post
    if len(args) >= 1 and args[0] in COMMANDS:
        return False

    with env.as_silent():
        try:
            http_parser.parse_args(env=env, args=args)
        except (Exception, SystemExit):
            return False
        else:
            return True
