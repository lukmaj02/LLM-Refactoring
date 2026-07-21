# SNAPSHOT METADATA
# sample_id: flask_028
# repo: flask
# file: data/repos/flask/src/flask/app.py
# function: Flask.test_request_context
# cc: 1 | mi: N/A | loc: 55
# extracted: 2026-05-01T11:47:37

def test_request_context(self, *args: t.Any, **kwargs: t.Any) -> RequestContext:
    """Create a :class:`~flask.ctx.RequestContext` for a WSGI
    environment created from the given values. This is mostly useful
    during testing, where you may want to run a function that uses
    request data without dispatching a full request.

    See :doc:`/reqcontext`.

    Use a ``with`` block to push the context, which will make
    :data:`request` point at the request for the created
    environment. ::

        with app.test_request_context(...):
            generate_report()

    When using the shell, it may be easier to push and pop the
    context manually to avoid indentation. ::

        ctx = app.test_request_context(...)
        ctx.push()
        ...
        ctx.pop()

    Takes the same arguments as Werkzeug's
    :class:`~werkzeug.test.EnvironBuilder`, with some defaults from
    the application. See the linked Werkzeug docs for most of the
    available arguments. Flask-specific behavior is listed here.

    :param path: URL path being requested.
    :param base_url: Base URL where the app is being served, which
        ``path`` is relative to. If not given, built from
        :data:`PREFERRED_URL_SCHEME`, ``subdomain``,
        :data:`SERVER_NAME`, and :data:`APPLICATION_ROOT`.
    :param subdomain: Subdomain name to append to
        :data:`SERVER_NAME`.
    :param url_scheme: Scheme to use instead of
        :data:`PREFERRED_URL_SCHEME`.
    :param data: The request body, either as a string or a dict of
        form keys and values.
    :param json: If given, this is serialized as JSON and passed as
        ``data``. Also defaults ``content_type`` to
        ``application/json``.
    :param args: other positional arguments passed to
        :class:`~werkzeug.test.EnvironBuilder`.
    :param kwargs: other keyword arguments passed to
        :class:`~werkzeug.test.EnvironBuilder`.
    """
    from .testing import EnvironBuilder

    builder = EnvironBuilder(self, *args, **kwargs)

    try:
        return self.request_context(builder.get_environ())
    finally:
        builder.close()
