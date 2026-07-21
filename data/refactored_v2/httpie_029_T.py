# === ARP Faza 4C - refactored code ===
# sample_id: httpie_029
# condition: T
# timestamp: 2026-06-04T14:07:57
# original_cc: 4, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def materialize_cookie(cookie: Cookie) -> Dict[str, Any]:
    materialized_cookie = {
        option: getattr(cookie, option)
        for option in KEPT_COOKIE_OPTIONS
    }

    if (
        cookie._rest.get('is_explicit_none')
        and materialized_cookie['domain'] == ''
    ):
        materialized_cookie['domain'] = None

    return materialized_cookie
