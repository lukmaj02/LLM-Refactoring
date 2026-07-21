# === ARP Faza 4C - refactored code ===
# sample_id: httpie_024
# condition: A
# timestamp: 2026-06-04T14:07:22
# original_cc: 8, original_mi: None
# changed_pct: 0.6364
# === END HEADER ===
def _clear_metadata(self, targets: List[str]) -> None:
    result_deps = self._collect_metadata()

    for target in targets:
        name, _, version = target.rpartition('-')
        normalized_name = PEP_503.sub("-", name).lower().replace('-', '_')
        if normalized_name in result_deps:
            self._remove_old_versions(result_deps[normalized_name], version)

def _collect_metadata(self) -> defaultdict:
    result_deps = defaultdict(list)
    for site_dir in get_site_paths(self.dir):
        for child in site_dir.iterdir():
            if child.suffix in {'.dist-info', '.egg-info'}:
                name, _, version = child.stem.rpartition('-')
                result_deps[name].append((version, child))
    return result_deps

def _remove_old_versions(self, versions_meta_paths: List[Tuple[str, Path]], current_version: str) -> None:
    for result_version, meta_path in versions_meta_paths:
        if current_version != result_version:
            shutil.rmtree(meta_path)