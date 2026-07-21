# === ARP Faza 4C - refactored code ===
# sample_id: flask_006
# condition: G
# timestamp: 2026-06-04T14:14:02
# original_cc: 13, original_mi: None
# changed_pct: 0.5474
# === END HEADER ===
def _get_dotenv_module_or_warn(path_arg: str | os.PathLike[str] | None) -> ModuleType | None:
    """Attempt to import dotenv, or show a warning if it's not installed
    and relevant .env files are present.
    """
    try:
        import dotenv
        return dotenv
    except ImportError:
        # Only show a warning if a file was explicitly passed or default files exist.
        if path_arg is not None or os.path.isfile(".env") or os.path.isfile(".flaskenv"):
            click.secho(
                " * Tip: There are .env files present. Install python-dotenv"
                " to use them.",
                fg="yellow",
                err=True,
            )
        return None


def _load_values_from_file(
    dotenv_module: ModuleType,
    file_path: str | os.PathLike[str],
    data: dict[str, str | None],
) -> None:
    """Load environment variables from a specific file path into the data dictionary."""
    if os.path.isfile(file_path):
        data |= dotenv_module.dotenv_values(file_path, encoding="utf-8")


def _load_default_dotenv_files(
    dotenv_module: ModuleType, data: dict[str, str | None]
) -> None:
    """Search for and load default .flaskenv and .env files."""
    for default_name in (".flaskenv", ".env"):
        if default_path := dotenv_module.find_dotenv(default_name, usecwd=True):
            _load_values_from_file(dotenv_module, default_path, data)


def _apply_loaded_env_vars(data: dict[str, str | None]) -> None:
    """Apply loaded environment variables to os.environ, respecting existing values."""
    for key, value in data.items():
        if key not in os.environ and value is not None:
            os.environ[key] = value


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
    dotenv_module = _get_dotenv_module_or_warn(path)

    if dotenv_module is None:
        return False

    data: dict[str, str | None] = {}

    if load_defaults:
        _load_default_dotenv_files(dotenv_module, data)

    if path is not None:
        _load_values_from_file(dotenv_module, path, data)

    _apply_loaded_env_vars(data)

    return bool(data)