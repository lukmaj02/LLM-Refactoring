# === ARP Faza 4C - refactored code ===
# sample_id: flask_017
# condition: A
# timestamp: 2026-06-04T14:14:57
# original_cc: 7, original_mi: None
# changed_pct: 0.6667
# === END HEADER ===
def _set_nested_key(config, key_parts, value):
    current = config
    *parts, tail = key_parts

    for part in parts:
        if part not in current:
            current[part] = {}
        current = current[part]

    current[tail] = value

def from_prefixed_env(
    self, prefix: str = "FLASK", *, loads: t.Callable[[str], t.Any] = json.loads
) -> bool:
    prefix = f"{prefix}_"

    for key in sorted(os.environ):
        if not key.startswith(prefix):
            continue

        value = os.environ[key]
        key = key.removeprefix(prefix)

        try:
            value = loads(value)
        except Exception:
            pass

        if "__" in key:
            _set_nested_key(self, key.split("__"), value)
        else:
            self[key] = value

    return True