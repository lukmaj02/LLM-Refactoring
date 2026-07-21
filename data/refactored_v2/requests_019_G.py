# === ARP Faza 4C - refactored code ===
# sample_id: requests_019
# condition: G
# timestamp: 2026-06-04T13:36:36
# original_cc: 5, original_mi: None
# changed_pct: 0.6222
# === END HEADER ===
def _normalize_auth_credential(value, name):
    """
    Normalizes an authentication credential (username or password) to bytes,
    issuing a DeprecationWarning if the input is not a string or bytes-like object.
    This maintains backwards compatibility for non-string types like integers.
    """
    # Handle non-basestring types (e.g., int) by converting to string and warning.
    if not isinstance(value, basestring):
        # Preserve the original warning message format for password,
        # which uses type(value) for the format string.
        format_arg = type(value) if name == "password" else value
        warnings.warn(
            "Non-string {}s will no longer be supported in Requests "
            "3.0.0. Please convert the object you've passed in ({!r}) to "
            "a string or bytes object in the near future to avoid "
            "problems.".format(name, format_arg),
            category=DeprecationWarning,
        )
        value = str(value)  # Convert to string

    # Ensure the value is bytes, encoding if it's a string.
    if isinstance(value, str):
        value = value.encode("latin1")
    return value


def _basic_auth_str(username, password):
    """Returns a Basic Auth string."""

    # "I want us to put a big-ol' comment on top of it that
    # says that this behaviour is dumb but we need to preserve
    # it because people are relying on it."
    #    - Lukasa
    #
    # These are here solely to maintain backwards compatibility
    # for things like ints. This will be removed in 3.0.0.
    username = _normalize_auth_credential(username, "username")
    password = _normalize_auth_credential(password, "password")
    # -- End Removal --

    authstr = "Basic " + to_native_string(
        b64encode(b":".join((username, password))).strip()
    )

    return authstr