# === ARP Faza 4C - refactored code ===
# sample_id: httpie_004
# condition: G
# timestamp: 2026-06-04T13:58:07
# original_cc: 24, original_mi: None
# changed_pct: 0.9592
# === END HEADER ===
def _write_message_separator(env: Environment):
    getattr(env.stdout, 'buffer', env.stdout).write(MESSAGE_SEPARATOR_BYTES)


def _initialize_downloader(args: argparse.Namespace, env: Environment) -> Optional[Downloader]:
    if args.download:
        args.follow = True  # --download implies --follow.
        downloader = Downloader(env, output_file=args.output_file, resume=args.download_resume)
        downloader.pre_request(args.headers)
        return downloader
    return None


def _process_message_iteration(
    message, args, env, processing_options, downloader,
    initial_request, final_response, current_