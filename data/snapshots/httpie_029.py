# SNAPSHOT METADATA
# sample_id: httpie_029
# repo: httpie
# file: data/repos/httpie/httpie/sessions.py
# function: materialize_cookie
# cc: 4 | mi: N/A | loc: 13
# extracted: 2026-05-01T11:47:36

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
