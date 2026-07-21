# === ARP Faza 4C - refactored code ===
# sample_id: flask_035
# condition: C
# timestamp: 2026-06-04T14:20:34
# original_cc: 3, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def get_send_file_max_age(self, filename: str | None) -> int | None:
    """Used by :func:`send_file` to determine the ``max_age`` cache
    value for a given file path if it wasn't passed.

    By default, this returns :data:`SEND_FILE_MAX_AGE_DEFAULT` from
    the configuration of :data:`~flask.current_app`. This defaults
    to ``None``, which tells the browser to use conditional requests
    instead of a timed cache, which is usually preferable.

    Note this is a duplicate of the same method in the Flask
    class.

    .. versionchanged:: 2.0
        The default configuration is ``None`` instead of 12 hours.

    .. versionadded:: 0.9
    """
    value = current_app.config["SEND_FILE_MAX_AGE_DEFAULT"]

    if value is None:
        return None

    if isinstance(value, timedelta):
        return int(value.total_seconds())

    return value  # type: ignore[no-any-return]