# === ARP Faza 4C - refactored code ===
# sample_id: flask_013
# condition: C
# timestamp: 2026-06-04T14:14:26
# original_cc: 10, original_mi: None
# changed_pct: 0.7959
# === END HEADER ===
def _find_root_spec(root_mod_name):
    """Return the root module spec, or None if it cannot be found."""
    try:
        root_spec = importlib.util.find_spec(root_mod_name)

        if root_spec is None:
            raise ValueError("not found")
    except (ImportError, ValueError):
        return None

    return root_spec


def _find_namespace_package_search_location(import_name, root_spec):
    """Find the search location for a namespace package."""
    package_spec = importlib.util.find_spec(import_name)

    if package_spec is not None and package_spec.submodule_search_locations:
        package_path = pathlib.Path(
            os.path.commonpath(package_spec.submodule_search_locations)
        )
        return next(
            location
            for location in root_spec.submodule_search_locations
            if package_path.is_relative_to(location)
        )

    return root_spec.submodule_search_locations[0]


def _find_package_path(import_name: str) -> str:
    """Find the path that contains the package or module."""
    root_mod_name, _, _ = import_name.partition(".")
    root_spec = _find_root_spec(root_mod_name)

    if root_spec is None:
        return os.getcwd()

    if not root_spec.submodule_search_locations:
        # module
        return os.path.dirname(root_spec.origin)  # type: ignore[type-var, return-value]

    if root_spec.origin is None or root_spec.origin == "namespace":
        # namespace package
        search_location = _find_namespace_package_search_location(import_name, root_spec)
        return os.path.dirname(search_location)

    # package with __init__.py
    return os.path.dirname(os.path.dirname(root_spec.origin))