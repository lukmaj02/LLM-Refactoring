# === ARP Faza 4C - refactored code ===
# sample_id: httpie_021
# condition: C
# timestamp: 2026-06-04T14:06:21
# original_cc: 7, original_mi: None
# changed_pct: 0.7500
# === END HEADER ===
def _handle_zero_length_file(
    env: Environment,
    file: Union[IO, 'MultipartEncoder'],
    callback: CallbackT,
    chunked: bool,
    content_length_header_value: Optional[int],
    read_event: threading.Event,
) -> Union[IO, bytes]:
    if is_stdin(file):
        observe_stdin_for_data_thread(env, file, read_event)

    if content_length_header_value is None and not chunked:
        return _read_file_with_selectors(file, read_event)

    return file


def _make_chunked_stream(
    file: Union[IO, 'MultipartEncoder'],
    callback: CallbackT,
    read_event: threading.Event,
) -> ChunkedStream:
    from requests_toolbelt import MultipartEncoder
    if isinstance(file, MultipartEncoder):
        return ChunkedMultipartUploadStream(encoder=file, event=read_event)
    return ChunkedUploadStream(stream=file, callback=callback, event=read_event)


def _prepare_file_for_upload(
    env: Environment,
    file: Union[IO, 'MultipartEncoder'],
    callback: CallbackT,
    chunked: bool = False,
    content_length_header_value: Optional[int] = None,
) -> Union[bytes, IO, ChunkedStream]:
    read_event = threading.Event()

    if not super_len(file):
        file = _handle_zero_length_file(
            env, file, callback, chunked, content_length_header_value, read_event
        )
    else:
        file.read = _wrap_function_with_callback(file.read, callback)

    if chunked:
        return _make_chunked_stream(file, callback, read_event)

    return file