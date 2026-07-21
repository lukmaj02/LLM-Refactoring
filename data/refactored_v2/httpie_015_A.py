# === ARP Faza 4C - refactored code ===
# sample_id: httpie_015
# condition: A
# timestamp: 2026-06-04T14:04:20
# original_cc: 10, original_mi: None
# changed_pct: 0.7121
# === END HEADER ===
def get_stream_type_and_kwargs(
    env: Environment,
    processing_options: ProcessingOptions,
    message_type: Type[HTTPMessage],
    headers: HTTPHeadersDict,
) -> Tuple[Type['BaseStream'], dict]:
    """Pick the right stream type and kwargs for it based on `env` and `args`.

    """
    is_stream = _determine_is_stream(processing_options, message_type, headers)
    prettify_groups = processing_options.get_prettify(env)

    if not env.stdout_isatty and not prettify_groups:
        return _get_raw_stream(is_stream)

    return _get_encoded_or_pretty_stream(
        env, processing_options, message_type, prettify_groups, is_stream
    )


def _determine_is_stream(processing_options, message_type, headers):
    is_stream = processing_options.stream
    if not is_stream and message_type is HTTPResponse:
        raw_content_type_header = headers.get('Content-Type', None)
        if raw_content_type_header:
            content_type_header, _ = parse_content_type_header(raw_content_type_header)
            is_stream = (content_type_header == 'text/event-stream')
    return is_stream


def _get_raw_stream(is_stream):
    stream_class = RawStream
    stream_kwargs = {
        'chunk_size': (
            RawStream.CHUNK_SIZE_BY_LINE
            if is_stream
            else RawStream.CHUNK_SIZE
        )
    }
    return stream_class, stream_kwargs


def _get_encoded_or_pretty_stream(env, processing_options, message_type, prettify_groups, is_stream):
    stream_class = EncodedStream
    stream_kwargs = {'env': env}

    if message_type is HTTPResponse:
        stream_kwargs.update({
            'mime_overwrite': processing_options.response_mime,
            'encoding_overwrite': processing_options.response_charset,
        })

    if prettify_groups:
        stream_class = PrettyStream if is_stream else BufferedPrettyStream
        stream_kwargs.update({
            'conversion': Conversion(),
            'formatting': Formatting(
                env=env,
                groups=prettify_groups,
                color_scheme=processing_options.style,
                explicit_json=processing_options.json,
                format_options=processing_options.format_options,
            )
        })

    return stream_class, stream_kwargs