# === ARP Faza 4C - refactored code ===
# sample_id: requests_018
# condition: T
# timestamp: 2026-06-04T13:38:40
# original_cc: 6, original_mi: None
# changed_pct: 0.0952
# === END HEADER ===
def merge_cookies(cookiejar, cookies):
    """Add cookies to cookiejar and returns a merged CookieJar.

    :param cookiejar: CookieJar object to add the cookies to.
    :param cookies: Dictionary or CookieJar object to be added.
    :rtype: CookieJar
    """
    if not isinstance(cookiejar, cookielib.CookieJar):
        raise ValueError("You can only merge into CookieJar")

    if isinstance(cookies, dict):
        cookiejar = cookiejar_from_dict(
            cookies, cookiejar=cookiejar, overwrite=False)
    elif isinstance(cookies, cookielib.CookieJar):
        try:
            cookiejar.update(cookies)
        except AttributeError:
            for cookie_in_jar in cookies:
                cookiejar.set_cookie(cookie_in_jar)

    return cookiejar
