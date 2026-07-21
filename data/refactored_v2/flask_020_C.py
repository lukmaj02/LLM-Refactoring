# === ARP Faza 4C - refactored code ===
# sample_id: flask_020
# condition: C
# timestamp: 2026-06-04T14:16:22
# original_cc: 5, original_mi: None
# changed_pct: 0.1111
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
    names: t.Iterable[str | None] = (None,)

    # A template may be rendered outside a request context.
    if request:
        names = chain(names, reversed(request.blueprints))

    # The values passed to render_template take precedence. Keep a
    # copy to re-apply after all context functions.
    orig_ctx = context.copy()

    for name in names:
        for func in self.template_context_processors.get(name, ()):
            context.update(self.ensure_sync(func)())

    context.update(orig_ctx)