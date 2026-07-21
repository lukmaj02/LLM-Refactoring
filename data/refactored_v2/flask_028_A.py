# === ARP Faza 4C - refactored code ===
# sample_id: flask_028
# condition: A
# timestamp: 2026-06-04T14:17:35
# original_cc: 1, original_mi: None
# changed_pct: 0.9091
# === END HEADER ===
def test_request_context(self, *args: t.Any, **kwargs: t.Any) -> RequestContext:
    from .testing import EnvironBuilder

    builder = EnvironBuilder(self, *args, **kwargs)
    environ = builder.get_environ()
    builder.close()

    return self.request_context(environ)