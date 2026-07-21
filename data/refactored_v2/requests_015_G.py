# === ARP Faza 4C - refactored code ===
# sample_id: requests_015
# condition: G
# timestamp: 2026-06-04T13:33:52
# original_cc: 11, original_mi: None
# changed_pct: 0.7872
# === END HEADER ===
def _detect_bom_encoding(sample):
    """Detects encoding based on Byte Order Mark (BOM) in the sample."""
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return "utf-32"
    if sample[:3] == codecs.BOM_UTF8:
        return "utf-8-sig"
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return "utf-16"
    return None


def _detect_null_byte_encoding(sample, nullcount):
    """Detects encoding based on null byte patterns in the sample."""
    if nullcount == 0:
        return "utf-8"
    if nullcount == 2:
        if sample[::2] == _null2:  # 1st and 3rd are null
            return "utf-16-be"
        if sample[1::2] == _null2:  # 2nd and 4th are null
            return "utf-16-le"
    if nullcount == 3:
        if sample[:3] == _null3:
            return "utf-32-be"
        if sample[1:] == _null3:
            return "utf-32-le"
    return None


def guess_json_utf(data):
    """
    :rtype: str
    """
    # JSON always starts with two ASCII characters, so detection is as
    # easy as counting the nulls and from their location and count
    # determine the encoding. Also detect a BOM, if present.
    sample = data[:4]

    encoding = _detect_bom_encoding(sample)
    if encoding:
        return encoding

    nullcount = sample.count(_null)
    encoding = _detect_null_byte_encoding(sample, nullcount)
    if encoding:
        return encoding

    return None