# === ARP Faza 4C - refactored code ===
# sample_id: requests_012
# condition: G
# timestamp: 2026-06-04T13:30:22
# original_cc: 17, original_mi: None
# changed_pct: 1.0000
# === END HEADER ===
def _get_length_from_fileno(obj):
    """Attempts to get the length of an object using its file descriptor."""
    try:
        fileno = obj.fileno()
    except (io.UnsupportedOperation, AttributeError):
        # AttributeError can occur for objects like Tarfile.extractfile()
        return None
    else:
        length = os.fstat(fileno).st_size
        # Warn if file is opened in text mode but length is determined by binary size.
        if "b" not in obj.mode:
            warnings.warn(
                (
                    "Requests has determined the content-length for this "
                    "request using the binary size of the file: however, the "
                    "