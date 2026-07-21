# === ARP Faza 4C - refactored code ===
# sample_id: httpie_002
# condition: T
# timestamp: 2026-06-04T14:00:39
# original_cc: 12, original_mi: None
# changed_pct: 0.0000
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
    files = args.files
    # Serialize JSON data, if needed.
    data = args.data
    auto_json = data and not args.form
    if (args.json or auto_json) and isinstance(data, dict):
        data = json_dict_to_request_body(data)

    # Finalize headers.
    headers = make_default_headers(args)
    if base_headers:
        headers.update(base_headers)
    headers.update(args.headers)
    if args.offline and args.chunked and 'Transfer-Encoding' not in headers:
        # When online, we let requests set the header instead to be able more
        # easily verify chunking is taking place.
        headers['Transfer-Encoding'] = 'chunked'
    headers = finalize_headers(headers)

    if (args.form and files) or args.multipart:
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
