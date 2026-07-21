# SNAPSHOT METADATA
# sample_id: flask_031
# repo: flask
# file: data/repos/flask/src/flask/sansio/scaffold.py
# function: Scaffold.context_processor
# cc: 1 | mi: N/A | loc: 15
# extracted: 2026-05-01T11:47:37

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
    self.template_context_processors[None].append(f)
    return f
