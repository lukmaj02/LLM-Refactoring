# === ARP Faza 4C - refactored code ===
# sample_id: requests_015
# condition: C
# timestamp: 2026-06-04T13:33:54
# original_cc: 11, original_mi: None
# changed_pct: 0.7895
# === END HEADER ===
def _guess_json_utf_from_bom(sample):
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return "utf-32"
    if sample[:3] == codecs.BOM_UTF8:
        return "utf-8-sig"
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return "utf-16"
    return None


def _guess_json_utf_from_nulls(sample, nullcount):
    if nullcount == 0:
        return "utf-8"
    if nullcount == 2:
        if sample[::2] == _null2:
            return "utf-16-be"
        if sample[1::2] == _null2:
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
    bom_encoding = _guess_json_utf_from_bom(sample)
    if bom_encoding is not None:
        return bom_encoding
    return _guess_json_utf_from_nulls(sample, sample.count(_null))