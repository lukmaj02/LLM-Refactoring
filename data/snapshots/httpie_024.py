# SNAPSHOT METADATA
# sample_id: httpie_024
# repo: httpie
# file: data/repos/httpie/httpie/manager/tasks/plugins.py
# function: PluginInstaller._clear_metadata
# cc: 8 | mi: N/A | loc: 20
# extracted: 2026-05-01T11:47:36

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
