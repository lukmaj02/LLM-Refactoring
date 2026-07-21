# === ARP Faza 4C - refactored code ===
# sample_id: flask_017
# condition: C
# timestamp: 2026-06-04T14:15:34
# original_cc: 7, original_mi: None
# changed_pct: 0.3667
# === END HEADER ===
def _try_load_value(value, loads):
    try:
        return loads(value)
    except Exception:
        return value


def _set_nested_value(current, key, value):
    *parts, tail = key.split("__")

    for part in parts:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[tail] = value


def from_prefixed_env(
    self, prefix: str = "FLASK", *, loads: t.Callable[[str], t.Any] = json.loads
) -> bool:
    """Load any environment variables that start with ``FLASK_``,
    dropping the prefix from the env key for the config key. Values
    are passed through a loading function to attempt to convert them
    to more specific types than strings.

    Keys are loaded in :func:`sorted` order.

    The default loading function attempts to parse values as any
    valid JSON type, including dicts and lists.

    Specific items in nested dicts can be set by separating the
    keys with double underscores (``__``). If an intermediate key
    doesn't exist, it will be initialized to an empty dict.

    :param prefix: Load env vars that start with this prefix,
        separated with an underscore (``_``).
    :param loads: Pass each string value to this function and use
        the returned value as the config value. If any error is
        raised it is ignored and the value remains a string. The
        default is :func:`json.loads`.

    .. versionadded:: 2.1
    """
    prefix = f"{prefix}_"

    for key in sorted(os.environ):
        if not key.startswith(prefix):
            continue

        value = _try_load_value(os.environ[key], loads)
        key = key.removeprefix(prefix)

        if "__" not in key:
            self[key] = value
        else:
            _set_nested_value(self, key, value)

    return True