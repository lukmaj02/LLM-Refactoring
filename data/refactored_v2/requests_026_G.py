# === ARP Faza 4C - refactored code ===
# sample_id: requests_026
# condition: G
# timestamp: 2026-06-04T13:44:55
# original_cc: 7, original_mi: None
# changed_pct: 0.3158
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

    if not overwrite:
        # Collect existing cookie names only if we are not overwriting