# SNAPSHOT METADATA
# sample_id: httpie_003
# repo: httpie
# file: data/repos/httpie/httpie/core.py
# function: raw_main
# cc: 27 | mi: N/A | loc: 112
# extracted: 2026-05-01T11:47:36

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

    if include_debug_info:
        print_debug_info(env)
        if args == ['--debug']:
            return ExitStatus.SUCCESS

    exit_status = ExitStatus.SUCCESS

    try:
        parsed_args = parser.parse_args(
            args=args,
            env=env,
        )
    except NestedJSONSyntaxError as exc:
        env.stderr.write(str(exc) + "\n")
        if include_traceback:
            raise
        exit_status = ExitStatus.ERROR
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
    else:
        check_updates(env)
        try:
            exit_status = main_program(
                args=parsed_args,
                env=env,
            )
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

            handle_generic_error(propagated_exc, annotation=annotation)
            exit_status = ExitStatus.ERROR
        except Exception as e:
            # TODO: Further distinction between expected and unexpected errors.
            handle_generic_error(e)
            exit_status = ExitStatus.ERROR

    return exit_status
