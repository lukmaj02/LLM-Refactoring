# === ARP Faza 4C - refactored code ===
# sample_id: httpie_002
# condition: G
# timestamp: 2026-06-04T13:56:51
# original_cc: 12, original_mi: None
# changed_pct: 0.7108
# === END HEADER ===
def _prepare_request_data(args: argparse.Namespace) -> tuple[Any, Optional[str]]:
    """
    Prepares the request body data, handling JSON serialization and
    multipart form data.

    Returns a tuple of (processed_data, content_type_from_multipart).
    content_type_from_multipart will be None if not multipart.
    """
    data = args.data
    content_type_from_multipart = None

    # Serialize JSON data, if needed.
    auto_json = data and not args.form
    if (args.json or auto_json) and isinstance(data, dict):
        data = json_dict_to_request_body(data)

    # Handle multipart data.
    if (args.form and args.files) or args.multipart:
        data, content_type_from_multipart = get_multipart_data_and_content_type(
            data=args.multipart_data,
            boundary=args.boundary,
            content_type=args.headers.get('Content-Type'),
        )
    return data, content_type_from_multipart


def _build_request_headers(
    args: argparse.Namespace,
    base_headers: HTTPHeadersDict = None,
    content_type_from_multipart: Optional[str] = None
) -> HTTPHeadersDict:
    """
    Builds and finalizes the request headers.
    """
    headers = make_default_headers(args)

    if base_headers:
        headers.update(base_headers)
    headers.update(args.headers)

    if args.offline and args.chunked and 'Transfer-Encoding' not in headers:
        # When online, we let requests set the header instead to be able more
        # easily verify chunking is taking place.
        headers['Transfer-Encoding'] = 'chunked'

    if content_type_from_multipart:
        headers['Content-Type'] = content_type_from_multipart

    return finalize_headers(headers)


def make_request_kwargs(
    env: Environment,
    args: argparse.Namespace,
    base_headers: HTTPHeadersDict = None,
    request_body_read_callback=lambda chunk: chunk
) -> dict:
    """
    Translate our `args` into `requests.Request` keyword arguments.
    """
    processed_data, content_type_from_multipart = _prepare_request_data(args)

    headers = _build_request_headers(
        args,
        base_headers,
        content_type_from_multipart
    )

    return {
        'method': args.method.lower(),
        'url': args.url,
        'headers': headers,
        'data': prepare_request_body(
            env,
            processed_data,
            body_read_callback=request_body_read_callback,
            chunked=args.chunked,
            offline=args.offline,
            content_length_header_value=headers.get('Content-Length'),
        ),
        'auth': args.auth,
        'params': args.params.items(),
    }