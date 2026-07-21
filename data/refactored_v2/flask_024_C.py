# === ARP Faza 4C - refactored code ===
# sample_id: flask_024
# condition: C
# timestamp: 2026-06-04T14:17:32
# original_cc: 2, original_mi: None
# changed_pct: 0.0000
# === END HEADER ===
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