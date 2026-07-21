# === ARP Faza 4C - refactored code ===
# sample_id: requests_008
# condition: C
# timestamp: 2026-06-04T13:26:19
# original_cc: 11, original_mi: None
# changed_pct: 0.7143
# === END HEADER ===
def _encode_param_value(v):
    return v.encode("utf-8") if isinstance(v, str) else v


def _encode_iterable_params(data):
    result = []
    for k, vs in to_key_val_list(data):
        if isinstance(vs, basestring) or not hasattr(vs, "__iter__"):
            vs = [vs]
        for v in vs:
            if v is not None:
                result.append(
                    (
                        _encode_param_value(k),
                        _encode_param_value(v),
                    )
                )
    return urlencode(result, doseq=True)


@staticmethod
def _encode_params(data):
    """Encode parameters in a piece of data.

    Will successfully encode parameters when passed as a dict or a list of
    2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
    if parameters are supplied as a dict.
    """
    if isinstance(data, (str, bytes)):
        return data
    if hasattr(data, "read"):
        return data
    if hasattr(data, "__iter__"):
        return _encode_iterable_params(data)
    return data