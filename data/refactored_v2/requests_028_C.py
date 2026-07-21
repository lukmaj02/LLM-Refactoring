# === ARP Faza 4C - refactored code ===
# sample_id: requests_028
# condition: C
# timestamp: 2026-06-04T13:49:44
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def __reduce__(self):
    """
    The __reduce__ method called when pickling the object must
    be the one from the JSONDecodeError (be it json/simplejson)
    as it expects all the arguments for instantiation, not just
    one like the IOError, and the MRO would by default call the
    __reduce__ method from the IOError due to the inheritance order.
    """
    return CompatJSONDecodeError.__reduce__(self)