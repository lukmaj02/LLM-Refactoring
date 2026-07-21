# SNAPSHOT METADATA
# sample_id: httpie_021
# repo: httpie
# file: data/repos/httpie/httpie/uploads.py
# function: _prepare_file_for_upload
# cc: 7 | mi: N/A | loc: 43
# extracted: 2026-05-01T11:47:36

def _prepare_file_for_upload(
    env: Environment,
    file: Union[IO, 'MultipartEncoder'],
    callback: CallbackT,
    chunked: bool = False,
    content_length_header_value: Optional[int] = None,
) -> Union[bytes, IO, ChunkedStream]:
    read_event = threading.Event()
    if not super_len(file):
        if is_stdin(file):
            observe_stdin_for_data_thread(env, file, read_event)

        # Zero-length -> assume stdin.
        if content_length_header_value is None and not chunked:
            # Read the whole stdin to determine `Content-Length`.
            #
            # TODO: Instead of opt-in --chunked, consider making
            #   `Transfer-Encoding: chunked` for STDIN opt-out via
            #   something like --no-chunked.
            #   This would be backwards-incompatible so wait until v3.0.0.
            #
            file = _read_file_with_selectors(file, read_event)
    else:
        file.read = _wrap_function_with_callback(
            file.read,
            callback
        )

    if chunked:
        from requests_toolbelt import MultipartEncoder
        if isinstance(file, MultipartEncoder):
            return ChunkedMultipartUploadStream(
                encoder=file,
                event=read_event,
            )
        else:
            return ChunkedUploadStream(
                stream=file,
                callback=callback,
                event=read_event
            )
    else:
        return file
