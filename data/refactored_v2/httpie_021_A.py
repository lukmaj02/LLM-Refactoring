# === ARP Faza 4C - refactored code ===
# sample_id: httpie_021
# condition: A
# timestamp: 2026-06-04T14:06:27
# original_cc: 7, original_mi: None
# changed_pct: 0.6744
# === END HEADER ===
def _prepare_file_for_upload(
    env: Environment,
    file: Union[IO, 'MultipartEncoder'],
    callback: CallbackT,
    chunked: bool = False,
    content_length_header_value: Optional[int] = None,
) -> Union[bytes, IO, ChunkedStream]:
    read_event = threading.Event()

    if not super_len(file):
        handle_zero_length_file(env, file, read_event, content_length_header_value, chunked)
    else:
        file.read = _wrap_function_with_callback(file.read, callback)

    if chunked:
        return create_chunked_stream(file, callback, read_event)
    else:
        return file


def handle_zero_length_file(env, file, read_event, content_length_header_value, chunked):
    if is_stdin(file):
        observe_stdin_for_data_thread(env, file, read_event)

    if content_length_header_value is None and not chunked:
        return _read_file_with_selectors(file, read_event)


def create_chunked_stream(file, callback, read_event):
    from requests_toolbelt import MultipartEncoder
    if isinstance(file, MultipartEncoder):
        return ChunkedMultipartUploadStream(encoder=file, event=read_event)
    else:
        return ChunkedUploadStream(stream=file, callback=callback, event=read_event)