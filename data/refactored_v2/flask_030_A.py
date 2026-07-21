# === ARP Faza 4C - refactored code ===
# sample_id: flask_030
# condition: A
# timestamp: 2026-06-04T14:18:07
# original_cc: 1, original_mi: None
# changed_pct: 0.2000
# === END HEADER ===
def dump(self, obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
    """Serialize data as JSON and write to a file.

    :param obj: The data to serialize.
    :param fp: A file opened for writing text. Should use the UTF-8
        encoding to be valid JSON.
    :param kwargs: May be passed to the underlying JSON library.
    """
    serialized_data = self.dumps(obj, **kwargs)
    fp.write(serialized_data)