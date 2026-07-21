# === ARP Faza 4C - refactored code ===
# sample_id: httpie_023
# condition: T
# timestamp: 2026-06-04T14:06:24
# original_cc: 7, original_mi: None
# changed_pct: 0.0333
# === END HEADER ===
def start(
    self,
    initial_url: str,
    final_response: requests.Response
) -> Tuple[RawStream, IO]:
    """
    Initiate and return a stream for `response` body  with progress
    callback attached. Can be called only once.

    :param initial_url: The original requested URL
    :param final_response: Initiated response object with headers already fetched

    :return: RawStream, output_file

    """
    assert not self.status.time_started

    # FIXME: some servers still might sent Content-Encoding: gzip
    # <https://github.com/httpie/cli/issues/423>
    try:
        total_size = int(final_response.headers['Content-Length'])
    except (KeyError, ValueError, TypeError):
        total_size = None

    if not self._output_file:
        self._output_file = self._get_output_file_from_response(
            initial_url=initial_url,
            final_response=final_response,
        )
    else:
        # `--output, -o` provided
        if self._resume and final_response.status_code == PARTIAL_CONTENT:
            total_size = parse_content_range(
                final_response.headers.get('Content-Range'),
                self._resumed_from
            )

        else:
            self._resumed_from = 0
            try:
                self._output_file.seek(0)
                self._output_file.truncate()
            except OSError:
                pass  # stdout

    output_options = OutputOptions.from_message(
        final_response, headers=False, body=True)
    stream = RawStream(
        msg=HTTPResponse(final_response),
        output_options=output_options,
        on_body_chunk_downloaded=self.chunk_downloaded,
    )

    self.status.started(
        output_file=self._output_file,
        resumed_from=self._resumed_from,
        total_size=total_size
    )

    return stream, self._output_file
