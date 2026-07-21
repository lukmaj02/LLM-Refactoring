# === ARP Faza 4C - refactored code ===
# sample_id: flask_013
# condition: A
# timestamp: 2026-06-04T14:14:04
# original_cc: 10, original_mi: None
# changed_pct: 0.7826
# === END HEADER ===
def _find_package_path(import_name: str) -> str:
    """Find the path that contains the package or module."""
    root_mod_name, _, _ = import_name.partition(".")

    root_spec = _get_root_spec(root_mod_name)
    if root_spec is None:
        return os.getcwd()

    if root_spec.submodule_search_locations:
        return _handle_submodule_search_locations(import_name, root_spec)
    else:
        return os.path.dirname(root_spec.origin)  # type: ignore[type-var, return-value]


def _get_root_spec(root_mod_name: str):
    try:
        root_spec = importlib.util.find_spec(root_mod_name)
        if root_spec is None:
            raise ValueError("not found")
        return root_spec
    except (ImportError, ValueError):
        return None


def _handle_submodule_search_locations(import_name: str, root_spec) -> str:
    if root_spec.origin is None or root_spec.origin == "namespace":
        return _handle_namespace_package(import_name, root_spec)
    else:
        return os.path.dirname(os.path.dirname(root_spec.origin))


def _handle_namespace_package(import_name: str, root_spec) -> str:
    package_spec = importlib.util.find_spec(import_name)
    if package_spec is not None and package_spec.submodule_search_locations:
        package_path = pathlib.Path(
            os.path.commonpath(package_spec.submodule_search_locations)
        )
        search_location = next(
            location
            for location in root_spec.submodule_search_locations
            if package_path.is_relative_to(location)
        )
    else:
        search_location = root_spec.submodule_search_locations[0]

    return os.path.dirname(search_location)