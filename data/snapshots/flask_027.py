# SNAPSHOT METADATA
# sample_id: flask_027
# repo: flask
# file: data/repos/flask/src/flask/app.py
# function: Flask.request_context
# cc: 1 | mi: N/A | loc: 15
# extracted: 2026-05-01T11:47:37

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
