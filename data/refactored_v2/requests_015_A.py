# === ARP Faza 4C - refactored code ===
# sample_id: requests_015
# condition: A
# timestamp: 2026-06-04T13:33:20
# original_cc: 11, original_mi: None
# changed_pct: 0.7442
# === END HEADER ===
def guess_json_utf(data):
    """
    :rtype: str
    """
    sample = data[:4]
    encoding = _detect_bom(sample)
    if encoding:
        return encoding

    nullcount = sample.count(_null)
    if nullcount == 0:
        return "utf-8"
    if nullcount == 2:
        return _detect_utf16(sample)
    if nullcount == 3:
        return _detect_utf32(sample)
    return None


def _detect_bom(sample):
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return "utf-32"
    if sample[:3] == codecs.BOM_UTF8:
        return "utf-8-sig"
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return "utf-16"
    return None


def _detect_utf16(sample):
    if sample[::2] == _null2:
        return "utf-16-be"
    if sample[1::2] == _null2:
        return "utf-16-le"
    return None


def _detect_utf32(sample):
    if sample[:3] == _null3:
        return "utf-32-be"
    if sample[1:] == _null3:
        return "utf-32-le"
    return None