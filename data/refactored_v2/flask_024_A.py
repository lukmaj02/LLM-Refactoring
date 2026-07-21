# === ARP Faza 4C - refactored code ===
# sample_id: flask_024
# condition: A
# timestamp: 2026-06-04T14:16:34
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
    cls = self.test_cli_runner_class or self._default_cli_runner_class()
    return cls(self, **kwargs)  # type: ignore

def _default_cli_runner_class(self):
    from .testing import FlaskCliRunner
    return FlaskCliRunner