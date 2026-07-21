# === ARP Faza 4C - refactored code ===
# sample_id: requests_016
# condition: G
# timestamp: 2026-06-04T13:35:26
# original_cc: 10, original_mi: None
# changed_pct: 0.7679
# === END HEADER ===
def _parse_urllib3_version(version_str):
    """Parses urllib3 version string into a (major, minor, patch) tuple."""
    parts = version_str.split(".")
    assert parts != ["dev"]  # Verify urllib3 isn't installed from git.

    # Sometimes, urllib3 only reports its version as 16.1.
    if len(parts) == 2:
        parts.append("0")
    return tuple(map(int, parts))


def _parse_generic_dependency_version(version_str):
    """Parses a generic dependency version string into a (major, minor, patch) tuple."""
    parts = version_str.split(".")[:3]
    return tuple(map(int, parts))


def _check_urllib3_compatibility(urllib3_version_str):
    """Checks urllib3 version for compatibility."""
    major, minor, patch = _parse_urllib3_version(urllib3_version_str)
    # urllib3 >= 1.21.1
    assert major >= 1
    if major == 1:
        assert minor >= 21


def _check_charset_dependency_compatibility(version_str, min_version, max_version):
    """
    Checks a character detection dependency version for compatibility.
    Returns True if compatible, False if version_str is None.
    Raises AssertionError if version_str is present but incompatible.
    """
    if not version_str:
        return False

    major, minor, patch = _parse_generic_dependency_version(version_str)
    assert min_version <= (major, minor, patch) < max_version
    return True


def check_compatibility(urllib3_version, chardet_version, charset_normalizer_version):
    _check_urllib3_compatibility(urllib3_version)

    chardet_ok = _check_charset_dependency_compatibility(
        chardet_version, (3, 0, 2), (6, 0, 0)
    )
    charset_normalizer_ok = _check_charset_dependency_compatibility(
        charset_normalizer_version, (2, 0, 0), (4, 0, 0)
    )

    if not chardet_ok and not charset_normalizer_ok:
        warnings.warn(
            "Unable to find acceptable character detection dependency "
            "(chardet or charset_normalizer).",
            RequestsDependencyWarning,
        )