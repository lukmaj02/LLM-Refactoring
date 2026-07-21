# === ARP Faza 4C - refactored code ===
# sample_id: flask_010
# condition: C
# timestamp: 2026-06-04T14:13:27
# original_cc: 10, original_mi: None
# changed_pct: 0.5968
# === END HEADER ===
def _get_loader(import_name: str) -> t.Any:
    """Find the loader for the given import name, or return None if not found."""
    try:
        spec = importlib.util.find_spec(import_name)

        if spec is None:
            raise ValueError
    except (ImportError, ValueError):
        return None

    return spec.loader


def _get_filepath_from_loader(loader: t.Any, import_name: str) -> str:
    """Get the file path from a loader, raising RuntimeError if unavailable."""
    if hasattr(loader, "get_filename"):
        return loader.get_filename(import_name)  # pyright: ignore

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


def get_root_path(import_name: str) -> str:
    """Find the root path of a package, or the path that contains a
    module. If it cannot be found, returns the current working
    directory.

    Not to be confused with the value returned by :func:`find_package`.

    :meta private:
    """
    # Module already imported and has a file attribute. Use that first.
    mod = sys.modules.get(import_name)

    if mod is not None and hasattr(mod, "__file__") and mod.__file__ is not None:
        return os.path.dirname(os.path.abspath(mod.__file__))

    loader = _get_loader(import_name)

    # Loader does not exist or we're referring to an unloaded main
    # module or a main module without path (interactive sessions), go
    # with the current working directory.
    if loader is None:
        return os.getcwd()

    filepath = _get_filepath_from_loader(loader, import_name)

    # filepath is import_name.py for a module, or __init__.py for a package.
    return os.path.dirname(os.path.abspath(filepath))  # type: ignore[no-any-return]