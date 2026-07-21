# === ARP Faza 4C - refactored code ===
# sample_id: flask_006
# condition: C
# timestamp: 2026-06-04T14:12:24
# original_cc: 13, original_mi: None
# changed_pct: 0.3067
# === END HEADER ===
def _dotenv_files_present(path):
    return path or os.path.isfile(".env") or os.path.isfile(".flaskenv")


def _apply_dotenv_data(data):
    for key, value in data.items():
        if key not in os.environ and value is not None:
            os.environ[key] = value


def _load_default_dotenv_files(dotenv):
    data: dict[str, str | None] = {}
    for default_name in (".flaskenv", ".env"):
        default_path = dotenv.find_dotenv(default_name, usecwd=True)
        if default_path:
            data |= dotenv.dotenv_values(default_path, encoding="utf-8")
    return data


def load_dotenv(
    path: str | os.PathLike[str] | None = None, load_defaults: bool = True
) -> bool:
    """Load "dotenv" files to set environment variables. A given path takes
    precedence over ``.env``, which takes precedence over ``.flaskenv``. After
    loading and combining these files, values are only set if the key is not
    already set in ``os.environ``.

    This is a no-op if `python-dotenv`_ is not installed.

    .. _python-dotenv: https://github.com/theskumar/python-dotenv#readme

    :param path: Load the file at this location.
    :param load_defaults: Search for and load the default ``.flaskenv`` and
        ``.env`` files.
    :return: ``True`` if at least one env var was loaded.

    .. versionchanged:: 3.1
        Added the ``load_defaults`` parameter. A given path takes precedence
        over default files.

    .. versionchanged:: 2.0
        The current directory is not changed to the location of the
        loaded file.

    .. versionchanged:: 2.0
        When loading the env files, set the default encoding to UTF-8.

    .. versionchanged:: 1.1.0
        Returns ``False`` when python-dotenv is not installed, or when
        the given path isn't a file.

    .. versionadded:: 1.0
    """
    try:
        import dotenv
    except ImportError:
        if _dotenv_files_present(path):
            click.secho(
                " * Tip: There are .env files present. Install python-dotenv"
                " to use them.",
                fg="yellow",
                err=True,
            )
        return False

    data: dict[str, str | None] = {}

    if load_defaults:
        data |= _load_default_dotenv_files(dotenv)

    if path is not None and os.path.isfile(path):
        data |= dotenv.dotenv_values(path, encoding="utf-8")

    _apply_dotenv_data(data)
    return bool(data)