# === ARP Faza 4C - refactored code ===
# sample_id: flask_022
# condition: A
# timestamp: 2026-06-04T14:16:11
# original_cc: 5, original_mi: None
# changed_pct: 0.5455
# === END HEADER ===
def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
    if self._should_load_options_early(ctx, args):
        _env_file_option.handle_parse_result(ctx, {}, [])
        _app_option.handle_parse_result(ctx, {}, [])

    return super().parse_args(ctx, args)

def _should_load_options_early(self, ctx: click.Context, args: list[str]) -> bool:
    return (not args and self.no_args_is_help) or (
        len(args) == 1 and args[0] in self.get_help_option_names(ctx)
    )