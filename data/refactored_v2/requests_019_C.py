# === ARP Faza 4C - refactored code ===
# sample_id: requests_019
# condition: C
# timestamp: 2026-06-04T13:38:33
# original_cc: 5, original_mi: None
# changed_pct: 0.5714
# === END HEADER ===
def _warn_non_string(value, name):
    if not isinstance(value, basestring):
        warnings.warn(
            "Non-string {}s will no longer be supported in Requests "
            "3.0.0. Please convert the object you've passed in ({!r}) to "
            "a string or bytes object in the near future to avoid "
            "problems.".format(name, value if name == "username" else type(value)),
            category=DeprecationWarning,
        )
        return str(value)
    return value


def _encode_latin1(value):
    if isinstance(value, str):
        return value.encode("latin1")
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
    username = _warn_non_string(username, "username")
    password = _warn_non_string(password, "password")
    # -- End Removal --

    username = _encode_latin1(username)
    password = _encode_latin1(password)

    authstr = "Basic " + to_native_string(
        b64encode(b":".join((username, password))).strip()
    )

    return authstr