# === ARP Faza 4C - refactored code ===
# sample_id: httpie_002
# condition: A
# timestamp: 2026-06-04T13:59:06
# original_cc: 12, original_mi: None
# changed_pct: 0.3962
# === END HEADER ===
def make_request_kwargs(
    env: Environment,
    args: argparse.Namespace,
    base_headers: HTTPHeadersDict = None,
    request_body_read_callback=lambda chunk: chunk
) -> dict:
    """
    Translate our `args` into `requests.Request` keyword arguments.

    """
    data = _prepare_data(args)
    headers = _prepare_headers(args, base_headers)

    if (args.form and args.files) or args.multipart:
        data, headers['Content-Type'] = get_multipart_data_and_content_type(
            data=args.multipart_data,
            boundary=args.boundary,
            content_type=args.headers.get('Content-Type'),
        )

    return {
        'method': args.method.lower(),
        'url': args.url,
        'headers': headers,
        'data': prepare_request_body(
            env,
            data,
            body_read_callback=request_body_read_callback,
            chunked=args.chunked,
            offline=args.offline,
            content_length_header_value=headers.get('Content-Length'),
        ),
        'auth': args.auth,
        'params': args.params.items(),
    }


def _prepare_data(args: argparse.Namespace) -> Any:
    data = args.data
    auto_json = data and not args.form
    if (args.json or auto_json) and isinstance(data, dict):
        data = json_dict_to_request_body(data)
    return data


def _prepare_headers(args: argparse.Namespace, base_headers: HTTPHeadersDict) -> HTTPHeadersDict:
    headers = make_default_headers(args)
    if base_headers:
        headers.update(base_headers)
    headers.update(args.headers)
    if args.offline and args.chunked and 'Transfer-Encoding' not in headers:
        headers['Transfer-Encoding'] = 'chunked'
    return finalize_headers(headers)