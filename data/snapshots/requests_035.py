# SNAPSHOT METADATA
# sample_id: requests_035
# repo: requests
# file: data/repos/requests/src/requests/sessions.py
# function: Session.delete
# cc: 1 | mi: N/A | loc: 9
# extracted: 2026-05-01T11:47:36

def delete(self, url, **kwargs):
    r"""Sends a DELETE request. Returns :class:`Response` object.

    :param url: URL for the new :class:`Request` object.
    :param \*\*kwargs: Optional arguments that ``request`` takes.
    :rtype: requests.Response
    """

    return self.request("DELETE", url, **kwargs)
