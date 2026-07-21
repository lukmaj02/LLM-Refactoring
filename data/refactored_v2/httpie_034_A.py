# === ARP Faza 4C - refactored code ===
# sample_id: httpie_034
# condition: A
# timestamp: 2026-06-04T14:09:51
# original_cc: 4, original_mi: None
# changed_pct: 0.8333
# === END HEADER ===
def to_name(self) -> str:
    operator_name = next((repr(key) for key, value in OPERATORS.items() if value is self), None)
    return operator_name if operator_name is not None else 'a ' + self.name.lower()