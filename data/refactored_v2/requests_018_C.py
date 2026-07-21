# === ARP Faza 4C - refactored code ===
# sample_id: requests_018
# condition: C
# timestamp: 2026-06-04T13:37:12
# original_cc: 6, original_mi: None
# changed_pct: 0.3750
# === END HEADER ===
def _merge_cookiejar(cookiejar, cookies):
    try:
        cookiejar.update(cookies)
    except AttributeError:
        for cookie_in_jar in cookies:
            cookiejar.set_cookie(cookie_in_jar)


def merge_cookies(cookiejar, cookies):
    """Add cookies to cookiejar and returns a merged CookieJar.

    :param cookiejar: CookieJar object to add the cookies to.
    :param cookies: Dictionary or CookieJar object to be added.
    :rtype: CookieJar
    """
    if not isinstance(cookiejar, cookielib.CookieJar):
        raise ValueError("You can only merge into CookieJar")

    if isinstance(cookies, dict):
        cookiejar = cookiejar_from_dict(cookies, cookiejar=cookiejar, overwrite=False)
    elif isinstance(cookies, cookielib.CookieJar):
        _merge_cookiejar(cookiejar, cookies)

    return cookiejar