# === ARP Faza 4C - refactored code ===
# sample_id: requests_033
# condition: C
# timestamp: 2026-06-04T13:55:29
# original_cc: 3, original_mi: None
# changed_pct: 0.2857
# === END HEADER ===
def extract_cookies_to_jar(jar, request, response):
    """Extract the cookies from the response into a CookieJar.

    :param jar: http.cookiejar.CookieJar (not necessarily a RequestsCookieJar)
    :param request: our own requests.Request object
    :param response: urllib3.HTTPResponse object
    """
    original_response = getattr(response, "_original_response", None)
    if not original_response:
        return
    req = MockRequest(request)
    res = MockResponse(original_response.msg)
    jar.extract_cookies(res, req)