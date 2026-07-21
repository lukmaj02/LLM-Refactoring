# === ARP Faza 4C - refactored code ===
# sample_id: httpie_001
# condition: C
# timestamp: 2026-06-04T13:58:51
# original_cc: 21, original_mi: None
# changed_pct: 0.7634
# === END HEADER ===
def _get_httpie_session(env, args):
    if not (args.session or args.session_read_only):
        return None
    return get_httpie_session(
        env=env,
        config_dir=env.config.directory,
        session_name=args.session or args.session_read_only,
        host=args.headers.get('Host'),
        url=args.url,
    )


def _apply_httpie_session(httpie_session, args, request_kwargs, requests_session):
    httpie_session.update_headers(request_kwargs['headers'])
    requests_session.cookies = httpie_session.cookies
    if args.auth_plugin:
        httpie_session.auth = {
            'type': args.auth_plugin.auth_type,
            'raw_auth': args.auth_plugin.raw_auth,
        }
    elif httpie_session.auth:
        request_kwargs['auth'] = httpie_session.auth


def _prepare_request(env, args, request_body_read_callback, httpie_session, requests_session):
    request_kwargs = make_request_kwargs(
        env,
        args=args,
        base_headers=httpie_session.headers if httpie_session else None,
        request_body_read_callback=request_body_read_callback,
    )

    if httpie_session:
        _apply_httpie_session(httpie_session, args, request_kwargs, requests_session)

    if args.debug:
        dump_request(request_kwargs)

    request = requests.Request(**request_kwargs)
    prepared_request = requests_session.prepare_request(request)
    transform_headers(request, prepared_request)

    if args.path_as_is:
        prepared_request.url = ensure_path_as_is(
            orig_url=args.url,
            prepped_url=prepared_request.url,
        )
    if args.compress and prepared_request.body:
        compress_request(
            request=prepared_request,
            always=args.compress > 1,
        )
    return prepared_request


def _send_request(args, requests_session, prepared_request, send_kwargs, send_kwargs_mergeable_from_env):
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
    return response


def _handle_redirect(args, response, response_count):
    if not response.next:
        return None, False
    if args.max_redirects and response_count == args.max_redirects:
        raise requests.TooManyRedirects
    if args.follow:
        return response.next, args.all
    return None, False


def _save_httpie_session(httpie_session, args, requests_session, expired_cookies):
    if httpie_session and (httpie_session.is_new() or not args.session_read_only):
        httpie_session.cookies = requests_session.cookies
        httpie_session.remove_cookies(expired_cookies)
        httpie_session.save()


def collect_messages(
    env: Environment,
    args: argparse.Namespace,
    request_body_read_callback: Callable[[bytes], None] = None,
) -> Iterable[RequestsMessage]:
    httpie_session = _get_httpie_session(env, args)

    send_kwargs = make_send_kwargs(args)
    send_kwargs_mergeable_from_env = make_send_kwargs_mergeable_from_env(args)
    requests_session = build_requests_session(
        ssl_version=args.ssl_version,
        ciphers=args.ciphers,
        verify=bool(send_kwargs_mergeable_from_env['verify']),
    )

    prepared_request = _prepare_request(
        env, args, request_body_read_callback, httpie_session, requests_session
    )

    response_count = 0
    expired_cookies = []

    while prepared_request:
        yield prepared_request
        if args.offline:
            break

        response = _send_request(
            args, requests_session, prepared_request, send_kwargs, send_kwargs_mergeable_from_env
        )
        expired_cookies += get_expired_cookies(response.headers.get('Set-Cookie', ''))
        response_count += 1

        next_request, should_yield_response = _handle_redirect(args, response, response_count)
        if next_request is not None:
            prepared_request = next_request
            if should_yield_response:
                yield response
            continue

        yield response
        break

    _save_httpie_session(httpie_session, args, requests_session, expired_cookies)