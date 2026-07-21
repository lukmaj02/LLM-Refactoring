# === ARP Faza 4C - refactored code ===
# sample_id: httpie_005
# condition: A
# timestamp: 2026-06-04T14:00:03
# original_cc: 10, original_mi: None
# changed_pct: 0.2969
# === END HEADER ===
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

    match = _match_content_range(content_range)
    content_range_dict = match.groupdict()
    first_byte_pos, last_byte_pos, instance_length = _extract_positions(content_range_dict)

    _validate_content_range(content_range, first_byte_pos, last_byte_pos, instance_length)
    _validate_requested_range(content_range, resumed_from, first_byte_pos, last_byte_pos, instance_length)

    return last_byte_pos + 1


def _match_content_range(content_range: str):
    pattern = (
        r'^bytes (?P<first_byte_pos>\d+)-(?P<last_byte_pos>\d+)'
        r'/(\*|(?P<instance_length>\d+))$'
    )
    match = re.match(pattern, content_range)
    if not match:
        raise ContentRangeError(
            f'Invalid Content-Range format {content_range!r}')
    return match


def _extract_positions(content_range_dict):
    first_byte_pos = int(content_range_dict['first_byte_pos'])
    last_byte_pos = int(content_range_dict['last_byte_pos'])
    instance_length = (
        int(content_range_dict['instance_length'])
        if content_range_dict['instance_length']
        else None
    )
    return first_byte_pos, last_byte_pos, instance_length


def _validate_content_range(content_range, first_byte_pos, last_byte_pos, instance_length):
    if (first_byte_pos > last_byte_pos
        or (instance_length is not None
            and instance_length <= last_byte_pos)):
        raise ContentRangeError(
            f'Invalid Content-Range returned: {content_range!r}')


def _validate_requested_range(content_range, resumed_from, first_byte_pos, last_byte_pos, instance_length):
    if (first_byte_pos != resumed_from
        or (instance_length is not None
            and last_byte_pos + 1 != instance_length)):
        raise ContentRangeError(
            f'Unexpected Content-Range returned ({content_range!r})'
            f' for the requested Range ("bytes={resumed_from}-")'
        )