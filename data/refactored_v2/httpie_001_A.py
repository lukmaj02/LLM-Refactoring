# === ARP Faza 4C - refactored code ===
# sample_id: httpie_001
# condition: A
# timestamp: 2026-06-04T13:58:49
# original_cc: 21, original_mi: None
# changed_pct: 0.6538
# === END HEADER ===
def collect_messages(
    env: Environment,
    args: argparse.Namespace,
    request_body_read_callback: Callable[[bytes], None] = None,
) -> Iterable[RequestsMessage]:
    httpie_session, httpie_session_headers = _initialize_httpie_session(env, args)

    request_kwargs = make_request_kwargs(
        env,
        args=args,
        base_headers=httpie_session_headers,
        request_body_read_callback=request_body_read_callback
    )
    send_kwargs = make_send_kwargs(args)
    send_kwargs_mergeable_from_env = make_send_kwargs_mergeable_from_env(args)
    requests_session = build_requests_session(
        ssl_version=args.ssl_version,
        ciphers=args.ciphers,
        verify=bool(send_kwargs_mergeable_from_env['verify'])
    )

    if httpie_session:
        _update_httpie_session(httpie_session, request_kwargs, requests_session, args)

    if args.debug:
        dump_request(request_kwargs)

    request = requests.Request(**request_kwargs)
    prepared_request = requests_session.prepare_request(request)
    transform_headers(request, prepared_request)
    _apply_path_as_is(args, prepared_request)
    _compress_request_if_needed(args, prepared_request)

    response_count = 0
    expired_cookies = []
    while prepared_request:
        yield prepared_request
        if not args.offline:
            response, expired_cookies = _send_request(
                args, requests_session, prepared_request, send_kwargs,
                send_kwargs_mergeable_from_env, expired_cookies
            )
            response_count += 1
            if _should_continue_following(args, response, response_count):
                prepared_request = response.next
                if args.all:
                    yield response
                continue
            yield response
        break

    _finalize_httpie_session(httpie_session, args, requests_session, expired_cookies)


def _initialize_httpie_session(env, args):
    httpie_session = None
    httpie_session_headers = None
    if args.session or args.session_read_only:
        httpie_session = get_httpie_session(
            env=env,
            config_dir=env.config.directory,
            session_name=args.session or args.session_read_only,
            host=args.headers.get('Host'),
            url=args.url,
        )
        httpie_session_headers = httpie_session.headers
    return httpie_session, httpie_session_headers


def _update_httpie_session(httpie_session, request_kwargs, requests_session, args):
    httpie_session.update_headers(request_kwargs['headers'])
    requests_session.cookies = httpie_session.cookies
    if args.auth_plugin:
        httpie_session.auth = {
            'type': args.auth_plugin.auth_type,
            'raw_auth': args.auth_plugin.raw_auth,
        }
    elif httpie_session.auth:
        request_kwargs['auth'] = httpie_session.auth


def _apply_path_as_is(args, prepared_request):
    if args.path_as_is:
        prepared_request.url = ensure_path_as_is(
            orig_url=args.url,
            prepped_url=prepared_request.url,
        )


def _compress_request_if_needed(args, prepared_request):
    if args.compress and prepared_request.body:
        compress_request(
            request=prepared_request,
            always=args.compress > 1,
        )


def _send_request(args, requests_session, prepared_request, send_kwargs, send_kwargs_mergeable_from_env, expired_cookies):
    send_kwargs_merged = requests_session.merge_environment_settings(
        url=prepared_request.url,
        **send_kwargs_mergeable_from_env,
    )
    with max_headers(args.max_headers):
        response = requests_session.send(
            request=prepared_request,
            **send_kwargs_merged,
            **send_kwargs,
        )
    response._httpie_headers_parsed_at = monotonic()
    expired_cookies += get_expired_cookies(
        response.headers.get('Set-Cookie', '')
    )
    return response, expired_cookies


def _should_continue_following(args, response, response_count):
    if response.next:
        if args.max_redirects and response_count == args.max_redirects:
            raise requests.TooManyRedirects
        if args.follow:
            return True
    return False


def _finalize_httpie_session(httpie_session, args, requests_session, expired_cookies):
    if httpie_session:
        if httpie_session.is_new() or not args.session_read_only:
            httpie_session.cookies = requests_session.cookies
            httpie_session.remove_cookies(expired_cookies)
            httpie_session.save()