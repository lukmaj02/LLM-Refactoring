# === ARP Faza 4C - refactored code ===
# sample_id: httpie_024
# condition: G
# timestamp: 2026-06-04T14:07:32
# original_cc: 8, original_mi: None
# changed_pct: 0.9500
# === END HEADER ===
def _normalize_package_name(self, raw_name: str) -> str:
        """Normalizes a package name to a canonical form for comparison."""
        # This logic matches the original function's normalization for target names.
        # PEP_503.sub("-", name) replaces [-._]+ with a single hyphen.
        # Then .lower()
        # Then .replace('-', '_') replaces hyphens with underscores.
        return PEP_503.sub("-", raw_name).lower().replace('-', '_')

    def _collect_existing_metadata(self) -> defaultdict[str, List[Tuple[str, Path]]]:
        """
        Collects existing plugin metadata from site directories,
        keyed by normalized