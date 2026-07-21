# === ARP Faza 4C - refactored code ===
# sample_id: flask_010
# condition: A
# timestamp: 2026-06-04T14:13:12
# original_cc: 10, original_mi: None
# changed_pct: 0.5818
# === END HEADER ===
def get_root_path(import_name: str) -> str:
    """Find the root path of a package, or the path that contains a
    module. If it cannot be found, returns the current working
    directory.

    Not to be confused with the value returned by :func:`find_package`.

    :meta private:
    """
    mod = sys.modules.get(import_name)
    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))

    loader = _get_loader(import_name)
    if loader is None:
        return os.getcwd()

    filepath = _get_filepath_from_loader(loader, import_name)
    if filepath is None:
        filepath = _get_filepath_from_import(import_name)

    return os.path.dirname(os.path.abspath(filepath))


def _get_loader(import_name: str):
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            raise ValueError
    except (ImportError, ValueError):
        return None
    return spec.loader


def _get_filepath_from_loader(loader, import_name: str):
    if hasattr(loader, "get_filename"):
        return loader.get_filename(import_name)  # pyright: ignore
    return None


def _get_filepath_from_import(import_name: str):
    __import__(import_name)
    mod = sys.modules[import_name]
    filepath = getattr(mod, "__file__", None)
    if filepath is None:
        raise RuntimeError(
            "No root path can be found for the provided module"
            f" {import_name!r}. This can happen because the module"
            " came from an import hook that does not provide file"
            " name information or because it's a namespace package."
            " In this case the root path needs to be explicitly"
            " provided."
        )
    return filepath