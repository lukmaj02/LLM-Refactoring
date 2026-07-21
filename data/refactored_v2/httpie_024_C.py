# === ARP Faza 4C - refactored code ===
# sample_id: httpie_024
# condition: C
# timestamp: 2026-06-04T14:07:12
# original_cc: 8, original_mi: None
# changed_pct: 0.5185
# === END HEADER ===
def _collect_installed_metadata(self, base_dir):
    result_deps = defaultdict(list)
    for site_dir in get_site_paths(base_dir):
        for child in site_dir.iterdir():
            if child.suffix in {'.dist-info', '.egg-info'}:
                name, _, version = child.stem.rpartition('-')
                result_deps[name].append((version, child))
    return result_deps

def _normalize_package_name(self, name):
    return PEP_503.sub("-", name).lower().replace('-', '_')

def _clear_metadata(self, targets: List[str]) -> None:
    # Due to an outstanding pip problem[0], we have to get rid of
    # existing metadata for old versions manually.
    # [0]: https://github.com/pypa/pip/issues/10727
    result_deps = self._collect_installed_metadata(self.dir)

    for target in targets:
        name, _, version = target.rpartition('-')
        name = self._normalize_package_name(name)
        if name not in result_deps:
            continue

        for result_version, meta_path in result_deps[name]:
            if version != result_version:
                shutil.rmtree(meta_path)