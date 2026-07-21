# === ARP Faza 4C - refactored code ===
# sample_id: flask_006
# condition: A
# timestamp: 2026-06-04T14:11:35
# original_cc: 13, original_mi: None
# changed_pct: 0.4886
# === END HEADER ===
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
    if not _is_dotenv_installed():
        _show_dotenv_tip(path)
        return False

    data = _load_default_dotenvs(load_defaults)
    data |= _load_custom_dotenv(path)

    _set_environment_variables(data)

    return bool(data)


def _is_dotenv_installed() -> bool:
    try:
        import dotenv
        return True
    except ImportError:
        return False


def _show_dotenv_tip(path: str | os.PathLike[str] | None) -> None:
    if path or os.path.isfile(".env") or os.path.isfile(".flaskenv"):
        click.secho(
            " * Tip: There are .env files present. Install python-dotenv"
            " to use them.",
            fg="yellow",
            err=True,
        )


def _load_default_dotenvs(load_defaults: bool) -> dict[str, str | None]:
    if not load_defaults:
        return {}

    import dotenv
    data = {}
    for default_name in (".flaskenv", ".env"):
        if default_path := dotenv.find_dotenv(default_name, usecwd=True):
            data |= dotenv.dotenv_values(default_path, encoding="utf-8")
    return data


def _load_custom_dotenv(path: str | os.PathLike[str] | None) -> dict[str, str | None]:
    if path is None or not os.path.isfile(path):
        return {}

    import dotenv
    return dotenv.dotenv_values(path, encoding="utf-8")


def _set_environment_variables(data: dict[str, str | None]) -> None:
    for key, value in data.items():
        if key not in os.environ and value is not None:
            os.environ[key] = value