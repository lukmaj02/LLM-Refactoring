# === ARP Faza 4C - refactored code ===
# sample_id: httpie_034
# condition: C
# timestamp: 2026-06-04T14:09:34
# original_cc: 4, original_mi: None
# changed_pct: 0.8333
# === END HEADER ===
def to_name(self) -> str:
    operator_names = {value: repr(key) for key, value in OPERATORS.items()}
    return operator_names.get(self, 'a ' + self.name.lower())