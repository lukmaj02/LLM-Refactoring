# === ARP Faza 4C - refactored code ===
# sample_id: requests_019
# condition: A
# timestamp: 2026-06-04T13:37:48
# original_cc: 5, original_mi: None
# changed_pct: 0.6905
# === END HEADER ===
def _warn_non_string(value, value_type):
    warnings.warn(
        f"Non-string {value_type}s will no longer be supported in Requests "
        f"3.0.0. Please convert the object you've passed in ({value!r}) to "
        f"a string or bytes object in the near future to avoid problems.",
        category=DeprecationWarning,
    )
    return str(value)


def _encode_if_str(value):
    return value.encode("latin1") if isinstance(value, str) else value


def _basic_auth_str(username, password):
    """Returns a Basic Auth string."""

    if not isinstance(username, basestring):
        username = _warn_non_string(username, "username")

    if not isinstance(password, basestring):
        password = _warn_non_string(type(password), "password")

    username = _encode_if_str(username)
    password = _encode_if_str(password)

    authstr = "Basic " + to_native_string(
        b64encode(b":".join((username, password))).strip()
    )

    return authstr