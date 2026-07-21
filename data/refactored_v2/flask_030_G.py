# === ARP Faza 4C - refactored code ===
# sample_id: flask_030
# condition: G
# timestamp: 2026-06-04T14:21:49
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def dump(self, obj: t.Any, fp: t.IO[str], **kwargs: t.Any) -> None:
    """Serialize data as JSON and write to a file.

    :param obj: The data to serialize.
    :param fp: A file opened for writing text. Should use the UTF-8
        encoding to be valid JSON.
    :param kwargs: May be passed to the underlying JSON library.
    """
    fp.write(self.dumps(obj, **kwargs))