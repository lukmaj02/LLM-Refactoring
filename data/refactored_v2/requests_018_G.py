# === ARP Faza 4C - refactored code ===
# sample_id: requests_018
# condition: G
# timestamp: 2026-06-04T13:36:17
# original_cc: 6, original_mi: None
# changed_pct: 0.4500
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
        # When 'cookies' is a dict, use cookiejar_from_dict with overwrite=False
        # This preserves existing cookies in 'cookiejar' if their names conflict.
        cookiejar = cookiejar_from_dict(cookies, cookie