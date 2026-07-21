# === ARP Faza 4C - refactored code ===
# sample_id: flask_013
# condition: G
# timestamp: 2026-06-04T14:17:02
# original_cc: 10, original_mi: None
# changed_pct: 0.7869
# === END HEADER ===
def _get_root_spec_or_none(import_name: str) -> importlib.machinery.ModuleSpec | None:
    """Attempt to find the module spec for the root module.

    Returns None if not found or an error occurs, indicating a fallback to CWD.
    """
    root_mod_name, _, _ = import_name.partition(".")
    try:
        root_spec = importlib.util.find_spec(root_mod_name)
        if root_spec is None:
            # Original logic treats None spec as a case for returning os.getcwd()
            return None
        return root_spec
    except (ImportError, ValueError):
        # Original logic catches these and returns os.getcwd()
        return None


def _get_namespace_package_path_from_spec(
    import_name: str, root_spec: importlib.machinery.ModuleSpec
) -> str:
    """Determine the path for a namespace package."""
    package_spec = importlib.util.find_spec(import_name)

    if package_spec is not None and package_spec.submodule_search_locations:
        # Pick the path in the namespace that contains the submodule.
        package_path = pathlib.Path(
            os.path.commonpath(package_spec.submodule_search_locations)
        )
        # The original code implies that package_path will always be relative to one of these.
        search_location = next(
            location
            for location in root_spec.submodule_search_locations
            if package_path.is_relative_to(location)
        )
    else:
        # Pick the first path if no specific submodule location is found.
        search_location = root_spec.submodule_search_locations[0]

    return os.path.dirname(search_location)


def _find_package_path(import_name: str) -> str:
    """Find the path that contains the package or module."""
    root_spec = _get_root_spec_or_none(import_name)

    if root_spec is None:
        return os.getcwd()

    if root_spec.submodule_search_locations:
        if root_spec.origin is None or root_spec.origin == "namespace":
            # namespace package
            return _get_namespace_package_path_from_spec(import_name, root_spec)
        else:
            # package with __init__.py
            # For a regular package, origin is the __init__.py file,
            # so we need its parent's parent directory.
            return os.path.dirname(os.path.dirname(root_spec.origin))
    else:
        # module (not a package, so origin is the module file itself)
        # For a module, origin is the .py file, so we need its parent directory.
        return os.path.dirname(root_spec.origin)  # type: ignore[type-var, return-value]