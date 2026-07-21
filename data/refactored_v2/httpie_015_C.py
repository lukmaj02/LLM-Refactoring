# === ARP Faza 4C - refactored code ===
# sample_id: httpie_015
# condition: C
# timestamp: 2026-06-04T14:04:06
# original_cc: 10, original_mi: None
# changed_pct: 0.7812
# === END HEADER ===
def _resolve_is_stream(processing_options, message_type, headers):
    if processing_options.stream:
        return True
    if message_type is not HTTPResponse:
        return False
    raw_content_type_header = headers.get('Content-Type', None)
    if not raw_content_type_header:
        return False
    content_type_header, _ = parse_content_type_header(raw_content_type_header)
    return content_type_header == 'text/event-stream'


def _get_raw_stream_kwargs(is_stream):
    return {
        'chunk_size': RawStream.CHUNK_SIZE_BY_LINE if is_stream else RawStream.CHUNK_SIZE
    }


def _get_encoded_stream_kwargs(env, processing_options, message_type):
    stream_kwargs = {'env': env}
    if message_type is HTTPResponse:
        stream_kwargs.update({
            'mime_overwrite': processing_options.response_mime,
            'encoding_overwrite': processing_options.response_charset,
        })
    return stream_kwargs


def _get_pretty_stream_kwargs(env, processing_options, prettify_groups):
    return {
        'conversion': Conversion(),
        'formatting': Formatting(
            env=env,
            groups=prettify_groups,
            color_scheme=processing_options.style,
            explicit_json=processing_options.json,
            format_options=processing_options.format_options,
        )
    }


def get_stream_type_and_kwargs(
    env: Environment,
    processing_options: ProcessingOptions,
    message_type: Type[HTTPMessage],
    headers: HTTPHeadersDict,
) -> Tuple[Type['BaseStream'], dict]:
    """Pick the right stream type and kwargs for it based on `env` and `args`.

    """
    is_stream = _resolve_is_stream(processing_options, message_type, headers)
    prettify_groups = processing_options.get_prettify(env)

    if not env.stdout_isatty and not prettify_groups:
        return RawStream, _get_raw_stream_kwargs(is_stream)

    stream_class = EncodedStream
    stream_kwargs = _get_encoded_stream_kwargs(env, processing_options, message_type)

    if prettify_groups:
        stream_class = PrettyStream if is_stream else BufferedPrettyStream
        stream_kwargs.update(_get_pretty_stream_kwargs(env, processing_options, prettify_groups))

    return stream_class, stream_kwargs