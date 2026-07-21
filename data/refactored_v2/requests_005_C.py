# === ARP Faza 4C - refactored code ===
# sample_id: requests_005
# condition: C
# timestamp: 2026-06-04T13:23:39
# original_cc: 21, original_mi: None
# changed_pct: 0.7619
# === END HEADER ===
def _encode_field_value(v):
    if not isinstance(v, bytes):
        v = str(v)
    return v.encode("utf-8") if isinstance(v, str) else v


def _encode_field_name(field):
    return field.decode("utf-8") if isinstance(field, bytes) else field


def _build_form_fields(fields):
    new_fields = []
    for field, val in fields:
        if isinstance(val, basestring) or not hasattr(val, "__iter__"):
            val = [val]
        for v in val:
            if v is not None:
                new_fields.append(
                    (_encode_field_name(field), _encode_field_value(v))
                )
    return new_fields


def _parse_file_tuple(k, v):
    ft = None
    fh = None
    if isinstance(v, (tuple, list)):
        if len(v) == 2:
            fn, fp = v
        elif len(v) == 3:
            fn, fp, ft = v
        else:
            fn, fp, ft, fh = v
    else:
        fn = guess_filename(v) or k
        fp = v
    return fn, fp, ft, fh


def _read_file_data(fp):
    if fp is None:
        return None
    if isinstance(fp, (str, bytes, bytearray)):
        return fp
    if hasattr(fp, "read"):
        return fp.read()
    return fp


def _build_file_fields(files):
    new_fields = []
    for k, v in files:
        fn, fp, ft, fh = _parse_file_tuple(k, v)
        fdata = _read_file_data(fp)
        if fdata is None:
            continue
        rf = RequestField(name=k, data=fdata, filename=fn, headers=fh)
        rf.make_multipart(content_type=ft)
        new_fields.append(rf)
    return new_fields


@staticmethod
def _encode_files(files, data):
    """Build the body for a multipart/form-data request.

    Will successfully encode files when passed as a dict or a list of
    tuples. Order is retained if data is a list of tuples but arbitrary
    if parameters are supplied as a dict.
    The tuples may be 2-tuples (filename, fileobj), 3-tuples (filename, fileobj, contentype)
    or 4-tuples (filename, fileobj, contentype, custom_headers).
    """
    if not files:
        raise ValueError("Files must be provided.")
    elif isinstance(data, basestring):
        raise ValueError("Data must not be a string.")

    fields = to_key_val_list(data or {})
    files = to_key_val_list(files or {})

    new_fields = _build_form_fields(fields) + _build_file_fields(files)

    body, content_type = encode_multipart_formdata(new_fields)
    return body, content_type