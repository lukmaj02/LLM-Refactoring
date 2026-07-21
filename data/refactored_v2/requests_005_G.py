# === ARP Faza 4C - refactored code ===
# sample_id: requests_005
# condition: G
# timestamp: 2026-06-04T13:24:58
# original_cc: 21, original_mi: None
# changed_pct: 0.9104
# === END HEADER ===
def _requests_encode_data_fields(data):
    """Helper to encode data fields for multipart/form-data."""
    processed_fields = []
    fields = to_key_val_list(data or {})
    for field, val in fields:
        # Ensure val is an iterable for consistent processing
        if isinstance(val, basestring) or not hasattr(val, "__iter__"):
            val = [val]
        for v in val:
            if v is not None:
                # Encode field name and value
                encoded_field = field.decode("utf-8") if isinstance(field, bytes) else field
                # Don't call str() on bytestrings: in Py3 it all