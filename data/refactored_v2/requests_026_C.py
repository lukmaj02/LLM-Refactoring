# === ARP Faza 4C - refactored code ===
# sample_id: requests_026
# condition: C
# timestamp: 2026-06-04T13:47:09
# original_cc: 7, original_mi: None
# changed_pct: 0.3333
# === END HEADER ===
def cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True):
    """Returns a CookieJar from a key/value dictionary.

    :param cookie_dict: Dict of key/values to insert into CookieJar.
    :param cookiejar: (optional) A cookiejar to add the cookies to.
    :param overwrite: (optional) If False, will not replace cookies
        already in the jar with new ones.
    :rtype: CookieJar
    """
    if cookiejar is None:
        cookiejar = RequestsCookieJar()

    if cookie_dict is None:
        return cookiejar

    names_from_jar = [cookie.name for cookie in cookiejar]
    for name, value in cookie_dict.items():
        if overwrite or name not in names_from_jar:
            cookiejar.set_cookie(create_cookie(name, value))

    return cookiejar