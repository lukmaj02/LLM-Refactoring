# SNAPSHOT METADATA
# sample_id: httpie_015
# repo: httpie
# file: data/repos/httpie/httpie/output/writer.py
# function: get_stream_type_and_kwargs
# cc: 10 | mi: N/A | loc: 52
# extracted: 2026-05-01T11:47:36

def get_stream_type_and_kwargs(
    env: Environment,
    processing_options: ProcessingOptions,
    message_type: Type[HTTPMessage],
    headers: HTTPHeadersDict,
) -> Tuple[Type['BaseStream'], dict]:
    """Pick the right stream type and kwargs for it based on `env` and `args`.

    """
    is_stream = processing_options.stream
    prettify_groups = processing_options.get_prettify(env)
    if not is_stream and message_type is HTTPResponse:
        # If this is a response, then check the headers for determining
        # auto-streaming.
        raw_content_type_header = headers.get('Content-Type', None)
        if raw_content_type_header:
            content_type_header, _ = parse_content_type_header(raw_content_type_header)
            is_stream = (content_type_header == 'text/event-stream')

    if not env.stdout_isatty and not prettify_groups:
        stream_class = RawStream
        stream_kwargs = {
            'chunk_size': (
                RawStream.CHUNK_SIZE_BY_LINE
                if is_stream
                else RawStream.CHUNK_SIZE
            )
        }
    else:
        stream_class = EncodedStream
        stream_kwargs = {
            'env': env,
        }
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
