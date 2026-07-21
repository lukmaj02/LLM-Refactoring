# SNAPSHOT METADATA
# sample_id: httpie_005
# repo: httpie
# file: data/repos/httpie/httpie/downloads.py
# function: parse_content_range
# cc: 10 | mi: N/A | loc: 56
# extracted: 2026-05-01T11:47:36

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

    if (first_byte_pos != resumed_from
        or (instance_length is not None
            and last_byte_pos + 1 != instance_length)):
        # Not what we asked for.
        raise ContentRangeError(
            f'Unexpected Content-Range returned ({content_range!r})'
            f' for the requested Range ("bytes={resumed_from}-")'
        )

    return last_byte_pos + 1
