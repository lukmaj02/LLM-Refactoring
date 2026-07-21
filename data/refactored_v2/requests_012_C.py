# === ARP Faza 4C - refactored code ===
# sample_id: requests_012
# condition: C
# timestamp: 2026-06-04T13:29:31
# original_cc: 17, original_mi: None
# changed_pct: 0.8676
# === END HEADER ===
def _get_length_from_fileno(o):
    """Try to determine total length using fileno/fstat."""
    try:
        fileno = o.fileno()
    except (io.UnsupportedOperation, AttributeError):
        return None

    total_length = os.fstat(fileno).st_size

    if hasattr(o, "mode") and "b" not in o.mode:
        warnings.warn(
            (
                "Requests has determined the content-length for this "
                "request using the binary size of the file: however, the "
                "file has been opened in text mode (i.e. without the 'b' "
                "flag in the mode). This may lead to an incorrect "
                "content-length. In Requests 3.0, support will be removed "
                "for files in text mode."
            ),
            FileModeWarning,
        )

    return total_length


def _get_total_length(o):
    """Determine total length of object using available attributes."""
    if hasattr(o, "__len__"):
        return len(o)
    if hasattr(o, "len"):
        return o.len
    if hasattr(o, "fileno"):
        return _get_length_from_fileno(o)
    return None


def _get_current_position(o, total_length):
    """Determine current position and update total_length if needed."""
    if not hasattr(o, "tell"):
        return 0, total_length

    try:
        current_position = o.tell()
    except OSError:
        return total_length if total_length is not None else 0, total_length

    if hasattr(o, "seek") and total_length is None:
        try:
            o.seek(0, 2)
            total_length = o.tell()
            o.seek(current_position or 0)
        except OSError:
            total_length = 0

    return current_position, total_length


def super_len(o):
    if isinstance(o, str):
        o = o.encode("utf-8")

    total_length = _get_total_length(o)
    current_position, total_length = _get_current_position(o, total_length)

    if total_length is None:
        total_length = 0

    return max(0, total_length - current_position)