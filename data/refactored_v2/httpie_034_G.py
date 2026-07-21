# === ARP Faza 4C - refactored code ===
# sample_id: httpie_034
# condition: G
# timestamp: 2026-06-04T14:10:47
# original_cc: 4, original_mi: None
# changed_pct: 0.8750
# === END HEADER ===
_TOKEN_KIND_TO_OPERATOR_KEY = {v: k for k, v in OPERATORS.items()}


def to_name(self) -> str:
    operator_key = _TOKEN_KIND_TO_OPERATOR_KEY.get(self)
    if operator_key is not None:
        return repr(operator_key)
    return 'a ' + self.name.lower()