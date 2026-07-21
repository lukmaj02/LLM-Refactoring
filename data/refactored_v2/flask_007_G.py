# === ARP Faza 4C - refactored code ===
# sample_id: flask_007
# condition: G
# timestamp: 2026-06-04T14:14:33
# original_cc: 12, original_mi: None
# changed_pct: 0.8431
# === END HEADER ===
def find_best_app(module: ModuleType) -> Flask:
    """Given a module instance this tries to find the best possible
    application in the module or raises an exception.
    """
    from . import Flask

    def _find_app_by_common_names() -> Flask | None:
        # Search for the most common names first.
        for attr_name in ("app", "application"):
            app = getattr(module, attr_name, None)

            if isinstance(app, Flask):
                return app
        return None

    def _find_single_app_instance() -> Flask | None:
        # Otherwise find the only object that is a Flask instance.
        matches = [v for