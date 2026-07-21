# SNAPSHOT METADATA
# sample_id: flask_026
# repo: flask
# file: data/repos/flask/src/flask/sansio/app.py
# function: App.debug
# cc: 2 | mi: N/A | loc: 5
# extracted: 2026-05-01T11:47:37

def debug(self, value: bool) -> None:
    self.config["DEBUG"] = value

    if self.config["TEMPLATES_AUTO_RELOAD"] is None:
        self.jinja_env.auto_reload = value
