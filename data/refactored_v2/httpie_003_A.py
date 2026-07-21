# === ARP Faza 4C - refactored code ===
# sample_id: httpie_003
# condition: A
# timestamp: 2026-06-04T13:59:20
# original_cc: 27, original_mi: None
# changed_pct: 0.6210
# === END HEADER ===
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

    if include_debug_info:
        print_debug_info(env)
        if args == ['--debug']:
            return ExitStatus.SUCCESS

    exit_status = ExitStatus.SUCCESS

    try:
        parsed_args = parser.parse_args(args=args, env=env)
    except (NestedJSONSyntaxError, KeyboardInterrupt, SystemExit) as exc:
        exit_status = _handle_parse_exception(exc, env, include_traceback)
    else:
        check_updates(env)
        exit_status = _execute_main_program(
            main_program, parsed_args, env, include_traceback
        )

    return exit_status


def _handle_parse_exception(exc, env, include_traceback):
    if isinstance(exc, NestedJSONSyntaxError):
        env.stderr.write(str(exc) + "\n")
        if include_traceback:
            raise
        return ExitStatus.ERROR
    elif isinstance(exc, KeyboardInterrupt):
        env.stderr.write('\n')
        if include_traceback:
            raise
        return ExitStatus.ERROR_CTRL_C
    elif isinstance(exc, SystemExit):
        if exc.code != ExitStatus.SUCCESS:
            env.stderr.write('\n')
            if include_traceback:
                raise
            return ExitStatus.ERROR
    return ExitStatus.SUCCESS


def _execute_main_program(main_program, parsed_args, env, include_traceback):
    exit_status = ExitStatus.SUCCESS
    try:
        exit_status = main_program(args=parsed_args, env=env)
    except KeyboardInterrupt:
        env.stderr.write('\n')
        if include_traceback:
            raise
        exit_status = ExitStatus.ERROR_CTRL_C
    except SystemExit as e:
        if e.code != ExitStatus.SUCCESS:
            env.stderr.write('\n')
            if include_traceback:
                raise
            exit_status = ExitStatus.ERROR
    except requests.Timeout:
        exit_status = ExitStatus.ERROR_TIMEOUT
        env.log_error(f'Request timed out ({parsed_args.timeout}s).')
    except requests.TooManyRedirects:
        exit_status = ExitStatus.ERROR_TOO_MANY_REDIRECTS
        env.log_error(
            f'Too many redirects'
            f' (--max-redirects={parsed_args.max_redirects}).'
        )
    except requests.exceptions.ConnectionError as exc:
        exit_status = _handle_connection_error(exc, env, include_traceback)
    except Exception as e:
        _handle_generic_error(e, env, include_traceback)
        exit_status = ExitStatus.ERROR
    return exit_status


def _handle_connection_error(exc, env, include_traceback):
    annotation = None
    original_exc = unwrap_context(exc)
    if isinstance(original_exc, socket.gaierror):
        if original_exc.errno == socket.EAI_AGAIN:
            annotation = '\nCouldn’t connect to a DNS server. Please check your connection and try again.'
        elif original_exc.errno == socket.EAI_NONAME:
            annotation = '\nCouldn’t resolve the given hostname. Please check the URL and try again.'
        propagated_exc = original_exc
    else:
        propagated_exc = exc

    _handle_generic_error(propagated_exc, env, include_traceback, annotation)
    return ExitStatus.ERROR


def _handle_generic_error(e, env, include_traceback, annotation=None):
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
    env.log_error(f'{type(e).__name__}: {msg}')
    if include_traceback:
        raise