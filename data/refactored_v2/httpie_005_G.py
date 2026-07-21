# === ARP Faza 4C - refactored code ===
# sample_id: httpie_005
# condition: G
# timestamp: 2026-06-04T13:58:19
# original_cc: 10, original_mi: None
# changed_pct: 0.5275
# === END HEADER ===
def _parse_content_range_header(content_range: str) -> Tuple[int, int, Optional[int]]:
    """
    Parses the Content-Range header string and extracts byte positions.
    Raises ContentRangeError if the format is invalid.
    """
    pattern = (
        r'^bytes (?P<first_byte_pos>\d+)-(?P<last_byte_pos>\d+)'
        r'/(\*|(?P<instance_length>\d+))$'
    )
    match = re.match(pattern, content_range)

    if not match:
        raise ContentRangeError(
            f'Invalid Content-Range format {content_range!r}')

    content_range_dict = match.groupdict()
    first_byte_pos = int(content_range_dict['first_byte_pos'])
    last_byte_pos = int(content_range_dict['last_byte_pos'])
    instance_length = (
        int(content_range_dict['instance_length'])
        if content_range_dict['instance_length']
        else None
    )
    return first_byte_pos, last_byte_pos, instance_length


def _validate_content_range_values(
    first_byte_pos: int,
    last_byte_pos: int,
    instance_length: Optional[int],
    content_range: str
):
    """
    Validates the extracted byte positions according to RFC2616.
    Raises ContentRangeError if the values are invalid.
    """
    # "A byte-content-range-spec with a byte-range-resp-spec whose
    # last- byte-pos value is less than its first-byte-pos value,
    # or whose instance-length value is less than or equal to its
    # last-byte-pos value, is invalid. The recipient of an invalid
    # byte-content-range- spec MUST ignore it and any content
    # transferred along with it."
    if (first_byte_pos > last_byte_pos
        or (instance_length is not None
            and instance_length <= last_byte_pos)):
        raise ContentRangeError(
            f'Invalid Content-Range returned: {content_range!r}')


def _validate_requested_range_match(
    first_byte_pos: int,
    last_byte_pos: int,
    instance_length: Optional[int],
    resumed_from: int,
    content_range: str
):
    """
    Validates if the Content-Range matches the requested Range.
    Raises ContentRangeError if there is a mismatch.
    """
    if (first_byte_pos != resumed_from
        or (instance_length is not None
            and last_byte_pos + 1 != instance_length)):
        # Not what we asked for.
        raise ContentRangeError(
            f'Unexpected Content-Range returned ({content_range!r})'
            f' for the requested Range ("bytes={resumed_from}-")'
        )


def parse_content_range(content_range: str, resumed_from: int) -> int:
    """
    Parse and validate Content-Range header.

    <https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html>

    :param content_range: the value of a Content-Range response header
                          eg. "bytes 21010-47021/47022"
    :param resumed_from: first byte pos. from the Range request header
    :return: total size of the response body when fully downloaded.

    """
    if content_range is None:
        raise ContentRangeError('Missing Content-Range')

    first_byte_pos, last_byte_pos, instance_length = _parse_content_range_header(content_range)

    _validate_content_range_values(first_byte_pos, last_byte_pos, instance_length, content_range)
    _validate_requested_range_match(first_byte_pos, last_byte_pos, instance_length, resumed_from, content_range)

    return last_byte_pos + 1