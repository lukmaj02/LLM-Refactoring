# === ARP Faza 4C - refactored code ===
# sample_id: httpie_029
# condition: A
# timestamp: 2026-06-04T14:08:51
# original_cc: 4, original_mi: None
# changed_pct: 0.7692
# === END HEADER ===
def materialize_cookie(cookie: Cookie) -> Dict[str, Any]:
    materialized_cookie = extract_cookie_options(cookie)
    if is_explicit_none(cookie, materialized_cookie):
        materialized_cookie['domain'] = None
    return materialized_cookie

def extract_cookie_options(cookie: Cookie) -> Dict[str, Any]:
    return {option: getattr(cookie, option) for option in KEPT_COOKIE_OPTIONS}

def is_explicit_none(cookie: Cookie, materialized_cookie: Dict[str, Any]) -> bool:
    return cookie._rest.get('is_explicit_none') and materialized_cookie['domain'] == ''