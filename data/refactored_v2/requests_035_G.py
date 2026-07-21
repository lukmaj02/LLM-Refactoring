# === ARP Faza 4C - refactored code ===
# sample_id: requests_035
# condition: G
# timestamp: 2026-06-04T13:54:32
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def delete(self, url, **kwargs):
    r"""Sends a DELETE request. Returns :class:`Response` object.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    return self.request("DELETE", url, **kwargs)