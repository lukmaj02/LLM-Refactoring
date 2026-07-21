# === ARP Faza 4C - refactored code ===
# sample_id: flask_024
# condition: G
# timestamp: 2026-06-04T14:20:27
# original_cc: 2, original_mi: None
# changed_pct: 0.3125
# === END HEADER ===
def test_cli_runner(self, **kwargs: t.Any) -> FlaskCliRunner:
    """Create a CLI runner for testing CLI commands.
    See :ref:`testing-cli`.

    Returns an instance of :attr:`test_cli_runner_class`, by default
    :class:`~flask.testing.FlaskCliRunner`. The Flask app object is
    passed as the first argument.

    .. versionadded:: 1.0
    """
    from .testing import FlaskCliRunner

    cls = self.test_cli_runner_class or FlaskCliRunner
    return cls(self, **kwargs)