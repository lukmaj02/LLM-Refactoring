# === ARP Faza 4C - refactored code ===
# sample_id: httpie_004
# condition: C
# timestamp: 2026-06-04T14:00:00
# original_cc: 24, original_mi: None
# changed_pct: 0.5285
# === END HEADER ===
def _setup_downloader(args, env):
    """Initialize and configure downloader if download mode is requested."""
    if not args.download:
        return None
    args.follow = True  # --download implies --follow.
    downloader = Downloader(env, output_file=args.output_file, resume=args.download_resume)
    downloader.pre_request(args.headers)
    return downloader


def _handle_request_message(message, output_options, initial_request, env):
    """Process a request message and return updated state."""
    if not initial_request:
        initial_request = message
    force_separator = False
    do_write_body = output_options.body
    if output_options.body:
        is_streamed_upload = not isinstance(message.body, (str, bytes))
        do_write_body = not is_streamed_upload
        force_separator = is_streamed_upload and env.stdout_isatty
    return initial_request, do_write_body, force_separator


def _handle_response_message(message, args, downloader, env):
    """Process a response message and return updated exit status."""
    exit_status = ExitStatus.SUCCESS
    if args.check_status or downloader:
        exit_status = http_status_to_exit_status(http_status=message.status_code, follow=args.follow)
        if exit_status != ExitStatus.SUCCESS and (not env.stdout_isatty or args.quiet == 1):
            env.log_error(f'HTTP {message.raw.status} {message.raw.reason}', level=LogLevel.WARNING)
    return exit_status


def _finalize_download(downloader, initial_request, final_response, exit_status, env):
    """Perform download finalization and return updated exit status."""
    if not (downloader and exit_status == ExitStatus.SUCCESS):
        return exit_status
    download_stream, download_to = downloader.start(
        initial_url=initial_request.url,
        final_response=final_response,
    )
    write_stream(stream=download_stream, outfile=download_to, flush=False)
    downloader.finish()
    if downloader.interrupted:
        exit_status = ExitStatus.ERROR
        env.log_error(
            f'Incomplete download: size={downloader.status.total_size};'
            f' downloaded={downloader.status.downloaded}'
        )
    return exit_status


def program(args: argparse.Namespace, env: Environment) -> ExitStatus:
    """
    The main program without error handling.

    """
    # TODO: Refactor and drastically simplify, especially so that the separator logic is elsewhere.
    exit_status = ExitStatus.SUCCESS
    downloader = None
    initial_request: Optional[requests.PreparedRequest] = None
    final_response: Optional[requests.Response] = None
    processing_options = ProcessingOptions.from_raw_args(args)

    def separate():
        getattr(env.stdout, 'buffer', env.stdout).write(MESSAGE_SEPARATOR_BYTES)

    def request_body_read_callback(chunk: bytes):
        should_pipe_to_stdout = bool(
            OUT_REQ_BODY in args.output_options
            and initial_request
            and chunk
        )
        if should_pipe_to_stdout:
            return write_raw_data(
                env,
                chunk,
                processing_options=processing_options,
                headers=initial_request.headers
            )

    try:
        downloader = _setup_downloader(args, env)
        messages = collect_messages(env, args=args, request_body_read_callback=request_body_read_callback)
        force_separator = False
        prev_with_body = False

        for message in messages:
            output_options = OutputOptions.from_message(message, args.output_options)
            do_write_body = output_options.body

            if prev_with_body and output_options.any() and (force_separator or not env.stdout_isatty):
                separate()

            force_separator = False

            if output_options.kind is RequestsMessageKind.REQUEST:
                initial_request, do_write_body, force_separator = _handle_request_message(
                    message, output_options, initial_request, env
                )
            else:
                final_response = message
                exit_status = _handle_response_message(message, args, downloader, env)

            write_message(
                requests_message=message,
                env=env,
                output_options=output_options._replace(body=do_write_body),
                processing_options=processing_options
            )
            prev_with_body = output_options.body

        if force_separator:
            separate()

        exit_status = _finalize_download(downloader, initial_request, final_response, exit_status, env)
        return exit_status

    finally:
        if downloader and not downloader.finished:
            downloader.failed()
        if args.output_file and args.output_file_specified:
            args.output_file.close()