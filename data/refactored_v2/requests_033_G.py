# === ARP Faza 4C - refactored code ===
# sample_id: requests_033
# condition: G
# timestamp: 2026-06-04T13:53:02
# original_cc: 3, original_mi: None
# changed_pct: 0.3500
# === END HEADER ===
def _has_original_response(response):
    """Check if the response object has a valid _original_response attribute."""
    return hasattr(response, "_original_response") and response._original_response


def extract_cookies_to_jar(jar, request, response):
    """Extract the cookies from the response into a CookieJar.

    :param jar: http.cookiejar.CookieJar (not necessarily a RequestsCookieJar)
    :param request: our own requests.Request object
    :param response: urllib3.HTTPResponse object
    """
    if not _has_original_response(response):
        return

    # the _original_response field is the wrapped httplib.HTTPResponse object,
    req = MockRequest(request)
    # pull out the HTTPMessage with the headers and put it in the mock:
    res = MockResponse(response._original_response.msg)
    jar.extract_cookies(res, req)