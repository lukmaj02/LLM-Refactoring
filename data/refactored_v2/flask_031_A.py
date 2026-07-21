# === ARP Faza 4C - refactored code ===
# sample_id: flask_031
# condition: A
# timestamp: 2026-06-04T14:18:20
# original_cc: 1, original_mi: None
# changed_pct: 0.2632
# === END HEADER ===
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
    self._add_context_processor(None, f)
    return f

def _add_context_processor(self, scope: ft.AppOrBlueprintKey, f: T_template_context_processor) -> None:
    """Helper function to add a context processor to the specified scope."""
    self.template_context_processors[scope].append(f)