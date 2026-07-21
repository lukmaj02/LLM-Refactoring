# === ARP Faza 4C - refactored code ===
# sample_id: httpie_029
# condition: G
# timestamp: 2026-06-04T14:08:57
# original_cc: 4, original_mi: None
# changed_pct: 0.7273
# === END HEADER ===
def _correct_materialized_cookie_domain(
    materialized_cookie: Dict[str, Any],
    original_cookie: Cookie
) -> None:
    """
    Corrects the 'domain' value in a materialized cookie dictionary
    if it was explicitly set to None but stored as an empty string.
    """
    if (
        original_cookie._rest.get('is_explicit_none')
        and materialized_cookie['domain'] == ''
    ):
        materialized_cookie['domain'] = None


def materialize_cookie(cookie: Cookie) -> Dict[str, Any]:
    materialized_cookie = {
        option: getattr(cookie, option)
        for option in KEPT_COOKIE_OPTIONS
    }
    _correct_materialized_cookie_domain(materialized_cookie, cookie)
    return materialized_cookie