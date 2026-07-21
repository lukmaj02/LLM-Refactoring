# === ARP Faza 4C - refactored code ===
# sample_id: httpie_034
# condition: T
# timestamp: 2026-06-04T14:08:31
# original_cc: 4, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def to_name(self) -> str:
    for key, value in OPERATORS.items():
        if value is self:
            return repr(key)
    else:
        return 'a ' + self.name.lower()
