# SNAPSHOT METADATA
# sample_id: flask_024
# repo: flask
# file: data/repos/flask/src/flask/app.py
# function: Flask.test_cli_runner
# cc: 2 | mi: N/A | loc: 16
# extracted: 2026-05-01T11:47:37

def test_cli_runner(self, **kwargs: t.Any) -> FlaskCliRunner:
    """Create a CLI runner for testing CLI commands.
    See :ref:`testing-cli`.

    Returns an instance of :attr:`test_cli_runner_class`, by default
    :class:`~flask.testing.FlaskCliRunner`. The Flask app object is
    passed as the first argument.

    .. versionadded:: 1.0
    """
    cls = self.test_cli_runner_class

    if cls is None:
        from .testing import FlaskCliRunner as cls

    return cls(self, **kwargs)  # type: ignore
