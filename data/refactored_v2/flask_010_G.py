# === ARP Faza 4C - refactored code ===
# sample_id: flask_010
# condition: G
# timestamp: 2026-06-04T14:15:52
# original_cc: 10, original_mi: None
# changed_pct: 0.9273
# === END HEADER ===
def _get_filepath_from_loader(import_name: str) -> str | None:
    """Attempts to get the file path using importlib.util.find_spec and loader methods.
    Raises RuntimeError if a module is found but has no __file__ attribute.
    Returns None if no spec or loader can be found.
    """
    spec = None
    try:
        spec = importlib.util.find_spec(import_name)
    except (ImportError, ValueError):
        # If find_spec itself fails, we can't get a loader this way.
        return None

    if spec is None or spec.loader is None:
        # If spec is None (e.g., not found) or