# === ARP Faza 4C - refactored code ===
# sample_id: requests_033
# condition: A
# timestamp: 2026-06-04T13:54:29
# original_cc: 3, original_mi: None
# changed_pct: 0.2667
# === END HEADER ===
def extract_cookies_to_jar(jar, request, response):
    """Extract the cookies from the response into a CookieJar.

    :param jar: http.cookiejar.CookieJar (not necessarily a RequestsCookieJar)
    :param request: our own requests.Request object
    :param response: urllib3.HTTPResponse object
    """
    if not _has_original_response(response):
        return
    req = MockRequest(request)
    res = MockResponse(response._original_response.msg)
    jar.extract_cookies(res, req)

def _has_original_response(response):
    return hasattr(response, "_original_response") and response._original_response