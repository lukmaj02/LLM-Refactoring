# === ARP Faza 4C - refactored code ===
# sample_id: httpie_004
# condition: A
# timestamp: 2026-06-04T13:59:39
# original_cc: 24, original_mi: None
# changed_pct: 0.4811
# === END HEADER ===
def program(args: argparse.Namespace, env: Environment) -> ExitStatus:
    """
    The main program without error handling.

    """
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
        if args.download:
            args.follow = True
            downloader = Downloader(env, output_file=args.output_file, resume=args.download_resume)
            downloader.pre_request(args.headers)

        messages = collect_messages(env, args=args, request_body_read_callback=request_body_read_callback)
        force_separator = False
        prev_with_body = False

        for message in messages:
            output_options = OutputOptions.from_message(message, args.output_options)
            do_write_body, force_separator = _process_message(
                message, output_options, initial_request, env, args, force_separator
            )
            if output_options.kind is RequestsMessageKind.REQUEST and not initial_request:
                initial_request = message
            if output_options.kind is not RequestsMessageKind.REQUEST:
                final_response = message
                exit_status = _handle_response_status(message, args, downloader, env, exit_status)

            write_message(
                requests_message=message,
                env=env,
                output_options=output_options._replace(body=do_write_body),
                processing_options=processing_options
            )
            prev_with_body = output_options.body

        if force_separator:
            separate()
        if downloader and exit_status == ExitStatus.SUCCESS:
            _finalize_download(downloader, initial_request, final_response, env, exit_status)

        return exit_status

    finally:
        if downloader and not downloader.finished:
            downloader.failed()
        if args.output_file and args.output_file_specified:
            args.output_file.close()


def _process_message(message, output_options, initial_request, env, args, force_separator):
    do_write_body = output_options.body
    if output_options.kind is RequestsMessageKind.REQUEST:
        if output_options.body:
            is_streamed_upload = not isinstance(message.body, (str, bytes))
            do_write_body = not is_streamed_upload
            force_separator = is_streamed_upload and env.stdout_isatty
    else:
        if output_options.any() and (force_separator or not env.stdout_isatty):
            separate()
        force_separator = False
    return do_write_body, force_separator


def _handle_response_status(message, args, downloader, env, exit_status):
    if args.check_status or downloader:
        exit_status = http_status_to_exit_status(http_status=message.status_code, follow=args.follow)
        if exit_status != ExitStatus.SUCCESS and (not env.stdout_isatty or args.quiet == 1):
            env.log_error(f'HTTP {message.raw.status} {message.raw.reason}', level=LogLevel.WARNING)
    return exit_status


def _finalize_download(downloader, initial_request, final_response, env, exit_status):
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