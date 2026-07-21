# === ARP Faza 4C - refactored code ===
# sample_id: httpie_003
# condition: C
# timestamp: 2026-06-04T13:59:36
# original_cc: 27, original_mi: None
# changed_pct: 0.7339
# === END HEADER ===
def _build_generic_error_message(e, annotation=None):
    msg = str(e)
    if hasattr(e, 'request'):
        request = e.request
        if hasattr(request, 'url'):
            msg = (
                f'{msg} while doing a {request.method}'
                f' request to URL: {request.url}'
            )
    if annotation:
        msg += annotation
    return f'{type(e).__name__}: {msg}'


def _get_connection_error_details(exc):
    annotation = None
    original_exc = unwrap_context(exc)
    if isinstance(original_exc, socket.gaierror):
        if original_exc.errno == socket.EAI_AGAIN:
            annotation = '\nCouldn\u2019t connect to a DNS server. Please check your connection and try again.'
        elif original_exc.errno == socket.EAI_NONAME:
            annotation = '\nCouldn\u2019t resolve the given hostname. Please check the URL and try again.'
        propagated_exc = original_exc
    else:
        propagated_exc = exc
    return propagated_exc, annotation


def _handle_keyboard_interrupt(env, include_traceback):
    env.stderr.write('\n')
    if include_traceback:
        raise
    return ExitStatus.ERROR_CTRL_C


def _handle_system_exit(e, env, include_traceback):
    if e.code != ExitStatus.SUCCESS:
        env.stderr.write('\n')
        if include_traceback:
            raise
        return ExitStatus.ERROR
    return ExitStatus.SUCCESS


def _parse_args(parser, args, env, include_traceback):
    try:
        parsed_args = parser.parse_args(args=args, env=env)
        return parsed_args, ExitStatus.SUCCESS
    except NestedJSONSyntaxError as exc:
        env.stderr.write(str(exc) + "\n")
        if include_traceback:
            raise
        return None, ExitStatus.ERROR
    except KeyboardInterrupt:
        return None, _handle_keyboard_interrupt(env, include_traceback)
    except SystemExit as e:
        return None, _handle_system_exit(e, env, include_traceback)


def _run_main_program(main_program, parsed_args, env, include_traceback, handle_generic_error):
    try:
        return main_program(args=parsed_args, env=env)
    except KeyboardInterrupt:
        return _handle_keyboard_interrupt(env, include_traceback)
    except SystemExit as e:
        return _handle_system_exit(e, env, include_traceback)
    except requests.Timeout:
        env.log_error(f'Request timed out ({parsed_args.timeout}s).')
        return ExitStatus.ERROR_TIMEOUT
    except requests.TooManyRedirects:
        env.log_error(
            f'Too many redirects'
            f' (--max-redirects={parsed_args.max_redirects}).'
        )
        return ExitStatus.ERROR_TOO_MANY_REDIRECTS
    except requests.exceptions.ConnectionError as exc:
        propagated_exc, annotation = _get_connection_error_details(exc)
        handle_generic_error(propagated_exc, annotation=annotation)
        return ExitStatus.ERROR
    except Exception as e:
        # TODO: Further distinction between expected and unexpected errors.
        handle_generic_error(e)
        return ExitStatus.ERROR


def raw_main(
    parser: argparse.ArgumentParser,
    main_program: Callable[[argparse.Namespace, Environment], ExitStatus],
    args: List[Union[str, bytes]] = sys.argv,
    env: Environment = Environment(),
    use_default_options: bool = True,
) -> ExitStatus:
    program_name, *args = args
    env.program_name = os.path.basename(program_name)
    args = decode_raw_args(args, env.stdin_encoding)

    if is_daemon_mode(args):
        return run_daemon_task(env, args)

    plugin_manager.load_installed_plugins(env.config.plugins_dir)

    if use_default_options and env.config.default_options:
        args = env.config.default_options + args

    include_debug_info = '--debug' in args
    include_traceback = include_debug_info or '--traceback' in args

    def handle_generic_error(e, annotation=None):
        env.log_error(_build_generic_error_message(e, annotation))
        if include_traceback:
            raise

    if include_debug_info:
        print_debug_info(env)
        if args == ['--debug']:
            return ExitStatus.SUCCESS

    parsed_args, exit_status = _parse_args(parser, args, env, include_traceback)

    if parsed_args is None:
        return exit_status

    check_updates(env)
    return _run_main_program(main_program, parsed_args, env, include_traceback, handle_generic_error)