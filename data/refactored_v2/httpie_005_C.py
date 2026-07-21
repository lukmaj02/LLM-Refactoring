# === ARP Faza 4C - refactored code ===
# sample_id: httpie_005
# condition: C
# timestamp: 2026-06-04T14:00:23
# original_cc: 10, original_mi: None
# changed_pct: 0.6897
# === END HEADER ===
_CONTENT_RANGE_PATTERN = re.compile(
    r'^bytes (?P<first_byte_pos>\d+)-(?P<last_byte_pos>\d+)'
    r'/(\*|(?P<instance_length>\d+))$'
)


def _parse_content_range_match(match):
    groups = match.groupdict()
    first_byte_pos = int(groups['first_byte_pos'])
    last_byte_pos = int(groups['last_byte_pos'])
    instance_length = int(groups['instance_length']) if groups['instance_length'] else None
    return first_byte_pos, last_byte_pos, instance_length


def _validate_content_range_spec(first_byte_pos, last_byte_pos, instance_length, content_range):
    if first_byte_pos > last_byte_pos:
        raise ContentRangeError(f'Invalid Content-Range returned: {content_range!r}')
    if instance_length is not None and instance_length <= last_byte_pos:
        raise ContentRangeError(f'Invalid Content-Range returned: {content_range!r}')


def _validate_content_range_matches_request(first_byte_pos, last_byte_pos, instance_length, resumed_from, content_range):
    if first_byte_pos != resumed_from:
        raise ContentRangeError(
            f'Unexpected Content-Range returned ({content_range!r})'
            f' for the requested Range ("bytes={resumed_from}-")'
        )
    if instance_length is not None and last_byte_pos + 1 != instance_length:
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

    match = _CONTENT_RANGE_PATTERN.match(content_range)
    if not match:
        raise ContentRangeError(f'Invalid Content-Range format {content_range!r}')

    first_byte_pos, last_byte_pos, instance_length = _parse_content_range_match(match)
    _validate_content_range_spec(first_byte_pos, last_byte_pos, instance_length, content_range)
    _validate_content_range_matches_request(first_byte_pos, last_byte_pos, instance_length, resumed_from, content_range)

    return last_byte_pos + 1