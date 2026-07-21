# === ARP Faza 4C - refactored code ===
# sample_id: flask_031
# condition: G
# timestamp: 2026-06-04T14:22:14
# original_cc: 1, original_mi: None
# changed_pct: 0.9500
# === END HEADER ===
def _register_callable_for_scope(self, target_attr_name: str, f: F) -> F:
        """Helper to register a callable to a list within a defaultdict attribute at the None scope."""
        getattr(self, target_attr_name)[None].append(f)
        return f

    @setupmethod
    def context_processor(
        self,
        f: T_template_context_processor,
    ) -> T_template_context_processor:
        """Registers a template context processor function. These functions run before
        rendering a template. The keys of the returned dict are added as variables
        available in the template.

        This is available on both app and blueprint objects. When used on an app, this
        is called for every rendered template. When used on a blueprint, this is called
        for templates rendered from the blueprint's views. To register with a blueprint
        and affect every template, use :meth:`.Blueprint.app_context_processor`.
        """
        return self._register_callable_for_scope("template_context_processors", f)