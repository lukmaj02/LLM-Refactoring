# === ARP Faza 4C - refactored code ===
# sample_id: flask_020
# condition: A
# timestamp: 2026-06-04T14:15:47
# original_cc: 5, original_mi: None
# changed_pct: 0.4667
# === END HEADER ===
def update_template_context(self, context: dict[str, t.Any]) -> None:
    """Update the template context with some commonly used variables.
    This injects request, session, config and g into the template
    context as well as everything template context processors want
    to inject.  Note that the as of Flask 0.6, the original values
    in the context will not be overridden if a context processor
    decides to return a value with the same key.

    :param context: the context as a dictionary that is updated in place
                    to add extra variables.
    """
    names = self._get_context_names()
    orig_ctx = context.copy()

    for name in names:
        self._update_context_with_processors(context, name)

    context.update(orig_ctx)

def _get_context_names(self) -> t.Iterable[str | None]:
    """Get the names for context processing, including request blueprints."""
    if request:
        return chain((None,), reversed(request.blueprints))
    return (None,)

def _update_context_with_processors(self, context: dict[str, t.Any], name: str | None) -> None:
    """Update the context with processors for a given name."""
    if name in self.template_context_processors:
        for func in self.template_context_processors[name]:
            context.update(self.ensure_sync(func)())