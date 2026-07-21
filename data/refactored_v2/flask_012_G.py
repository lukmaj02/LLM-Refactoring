# === ARP Faza 4C - refactored code ===
# sample_id: flask_012
# condition: G
# timestamp: 2026-06-04T14:16:29
# original_cc: 23, original_mi: None
# changed_pct: 0.9810
# === END HEADER ===
def _combine_subdomains(parent_subdomain: str | None, child_subdomain: str | None) -> str | None:
    """Combines a parent subdomain with a child subdomain."""
    if parent_subdomain is not None and child_subdomain is not None:
        return f"{child_subdomain}.{parent_subdomain}"
    return child_subdomain if child_subdomain is not None else parent_subdomain


def _combine_url_prefixes(parent_prefix: str | None, child_prefix: str | None) -> str | None:
    """Combines a parent URL prefix with a child URL prefix."""
    if parent_prefix is not None and child_prefix is not None:
        return