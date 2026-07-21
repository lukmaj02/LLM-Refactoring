# === ARP Faza 4C - refactored code ===
# sample_id: requests_016
# condition: C
# timestamp: 2026-06-04T13:35:38
# original_cc: 10, original_mi: None
# changed_pct: 0.4500
# === END HEADER ===
def _parse_version(version_string):
    parts = version_string.split(".")[:3]
    return tuple(int(x) for x in parts)


def _check_urllib3_compatibility(urllib3_version):
    urllib3_version = urllib3_version.split(".")
    assert urllib3_version != ["dev"]  # Verify urllib3 isn't installed from git.

    # Sometimes, urllib3 only reports its version as 16.1.
    if len(urllib3_version) == 2:
        urllib3_version.append("0")

    major, minor, patch = (int(x) for x in urllib3_version)  # noqa: F811
    # urllib3 >= 1.21.1
    assert major >= 1
    if major == 1:
        assert minor >= 21


def _check_charset_dependency(chardet_version, charset_normalizer_version):
    if chardet_version:
        version = _parse_version(chardet_version)
        # chardet_version >= 3.0.2, < 6.0.0
        assert (3, 0, 2) <= version < (6, 0, 0)
    elif charset_normalizer_version:
        version = _parse_version(charset_normalizer_version)
        # charset_normalizer >= 2.0.0 < 4.0.0
        assert (2, 0, 0) <= version < (4, 0, 0)
    else:
        warnings.warn(
            "Unable to find acceptable character detection dependency "
            "(chardet or charset_normalizer).",
            RequestsDependencyWarning,
        )


def check_compatibility(urllib3_version, chardet_version, charset_normalizer_version):
    _check_urllib3_compatibility(urllib3_version)
    _check_charset_dependency(chardet_version, charset_normalizer_version)