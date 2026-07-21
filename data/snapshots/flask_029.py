# SNAPSHOT METADATA
# sample_id: flask_029
# repo: flask
# file: data/repos/flask/src/flask/sansio/scaffold.py
# function: Scaffold.static_folder
# cc: 2 | mi: N/A | loc: 5
# extracted: 2026-05-01T11:47:37

def static_folder(self, value: str | os.PathLike[str] | None) -> None:
    if value is not None:
        value = os.fspath(value).rstrip(r"\/")

    self._static_folder = value
