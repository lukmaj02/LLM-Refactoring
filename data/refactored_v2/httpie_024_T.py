# === ARP Faza 4C - refactored code ===
# sample_id: httpie_024
# condition: T
# timestamp: 2026-06-04T14:06:38
# original_cc: 8, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def _clear_metadata(self, targets: List[str]) -> None:
    # Due to an outstanding pip problem[0], we have to get rid of
    # existing metadata for old versions manually.
    # [0]: https://github.com/pypa/pip/issues/10727
    result_deps = defaultdict(list)
    for site_dir in get_site_paths(self.dir):
        for child in site_dir.iterdir():
            if child.suffix in {'.dist-info', '.egg-info'}:
                name, _, version = child.stem.rpartition('-')
                result_deps[name].append((version, child))

    for target in targets:
        name, _, version = target.rpartition('-')
        name = PEP_503.sub("-", name).lower().replace('-', '_')
        if name not in result_deps:
            continue

        for result_version, meta_path in result_deps[name]:
            if version != result_version:
                shutil.rmtree(meta_path)
