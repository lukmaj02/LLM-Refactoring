# === ARP Faza 4C - refactored code ===
# sample_id: requests_016
# condition: A
# timestamp: 2026-06-04T13:34:59
# original_cc: 10, original_mi: None
# changed_pct: 0.7429
# === END HEADER ===
def check_compatibility(urllib3_version, chardet_version, charset_normalizer_version):
    _check_urllib3_compatibility(urllib3_version)
    if chardet_version:
        _check_chardet_compatibility(chardet_version)
    elif charset_normalizer_version:
        _check_charset_normalizer_compatibility(charset_normalizer_version)
    else:
        warnings.warn(
            "Unable to find acceptable character detection dependency "
            "(chardet or charset_normalizer).",
            RequestsDependencyWarning,
        )


def _check_urllib3_compatibility(urllib3_version):
    urllib3_version = urllib3_version.split(".")
    assert urllib3_version != ["dev"]  # Verify urllib3 isn't installed from git.

    if len(urllib3_version) == 2:
        urllib3_version.append("0")

    major, minor, patch = map(int, urllib3_version)
    assert major >= 1
    if major == 1:
        assert minor >= 21


def _check_chardet_compatibility(chardet_version):
    major, minor, patch = map(int, chardet_version.split(".")[:3])
    assert (3, 0, 2) <= (major, minor, patch) < (6, 0, 0)


def _check_charset_normalizer_compatibility(charset_normalizer_version):
    major, minor, patch = map(int, charset_normalizer_version.split(".")[:3])
    assert (2, 0, 0) <= (major, minor, patch) < (4, 0, 0)