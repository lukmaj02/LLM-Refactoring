# === ARP Faza 4C - refactored code ===
# sample_id: flask_022
# condition: C
# timestamp: 2026-06-04T14:16:45
# original_cc: 5, original_mi: None
# changed_pct: 0.4286
# === END HEADER ===
def _is_help_only_invocation(self, ctx: click.Context, args: list[str]) -> bool:
    return (not args and self.no_args_is_help) or (
        len(args) == 1 and args[0] in self.get_help_option_names(ctx)
    )

def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
    if self._is_help_only_invocation(ctx, args):
        # Attempt to load --env-file and --app early in case they
        # were given as env vars. Otherwise no_args_is_help will not
        # see commands from app.cli.
        _env_file_option.handle_parse_result(ctx, {}, [])
        _app_option.handle_parse_result(ctx, {}, [])

    return super().parse_args(ctx, args)