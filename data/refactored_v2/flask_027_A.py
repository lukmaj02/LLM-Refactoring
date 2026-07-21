# === ARP Faza 4C - refactored code ===
# sample_id: flask_027
# condition: A
# timestamp: 2026-06-04T14:17:12
# original_cc: 1, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
def request_context(self, environ: WSGIEnvironment) -> RequestContext:
    """Create a :class:`~flask.ctx.RequestContext` representing a
    WSGI environment. Use a ``with`` block to push the context,
    which will make :data:`request` point at this request.

    See :doc:`/reqcontext`.

    Typically you should not call this from your own code. A request
    context is automatically pushed by the :meth:`wsgi_app` when
    handling a request. Use :meth:`test_request_context` to create
    an environment and context instead of this method.

    :param environ: a WSGI environment
    """
    return RequestContext(self, environ)