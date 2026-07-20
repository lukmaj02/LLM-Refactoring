from __future__ import annotations
import logging
import shutil
import tempfile
from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
log = logging.getLogger(__name__)
DEFAULT_IGNORES: tuple[str,
                       ...] = ('.git',
                               '.tox',
                               '.mypy_cache',
                               '.pytest_cache',
                               '.ruff_cache',
                               '__pycache__',
                               'node_modules',
                               '.venv',
                               'venv',
                               'build',
                               'dist',
                               'htmlcov',
                               '.coverage')


def _ignore_factory(extra: Iterable[str] = ()) -> 'shutil._IgnoreFn':
    patterns = set(DEFAULT_IGNORES) | set(extra)

    def _ignore(_dir: str, names: list[str]) -> list[str]:
        return [n for n in names if n in patterns]
    return _ignore


def copy_repo_to_temp(repo_root: Path | str, *,
                      extra_ignores: Iterable[str] = (), prefix: str = 'arp_4c_') -> Path:
    repo_root = Path(repo_root)
    if not repo_root.is_dir():
        raise FileNotFoundError(f'Repo not found: {repo_root}')
    tmp_parent = Path(tempfile.mkdtemp(prefix=prefix))
    dest = tmp_parent / repo_root.name
    shutil.copytree(repo_root, dest, ignore=_ignore_factory(extra_ignores), symlinks=False)
    return dest


@dataclass
class PatchResult:
    success: bool
    file_path: Path
    original_slice: str
    new_slice: str
    detail: str = ''


def _detect_indent(lines: list[str]) -> str:
    indents = []
    for ln in lines:
        if ln.strip():
            indents.append(len(ln) - len(ln.lstrip(' \t')))
    if not indents:
        return ''
    width = min(indents)
    for ln in lines:
        if ln.strip():
            return ln[:width]
    return ''


def _reindent_snippet(snippet: str, indent: str) -> str:
    if not indent:
        return snippet
    lines = snippet.splitlines(keepends=True)
    first_non_blank = next((ln for ln in lines if ln.strip()), '')
    if first_non_blank.startswith(indent):
        return snippet
    new_lines = []
    for ln in lines:
        if ln.strip():
            new_lines.append(indent + ln)
        else:
            new_lines.append(ln)
    return ''.join(new_lines)


def patch_function_in_file(target_file: Path | str, refactored_code: str,
                           start_line: int, end_line: int, *, reindent: bool = True) -> PatchResult:
    target_file = Path(target_file)
    if not target_file.is_file():
        return PatchResult(success=False, file_path=target_file, original_slice='',
                           new_slice=refactored_code, detail=f'file not found: {target_file}')
    text = target_file.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    if start_line < 1 or end_line < start_line or end_line > len(lines):
        return PatchResult(success=False, file_path=target_file, original_slice='', new_slice=refactored_code,
                           detail=f'invalid line range {start_line}-{end_line} (file has {len(lines)} lines)')
    head = lines[:start_line - 1]
    original_slice_lines = lines[start_line - 1:end_line]
    original_slice = ''.join(original_slice_lines)
    tail = lines[end_line:]
    snippet = refactored_code
    if reindent:
        indent = _detect_indent(original_slice_lines)
        snippet = _reindent_snippet(snippet, indent)
    if not snippet.endswith('\n'):
        snippet += '\n'
    new_text = ''.join(head) + snippet + ''.join(tail)
    target_file.write_text(new_text, encoding='utf-8')
    return PatchResult(success=True, file_path=target_file, original_slice=original_slice,
                       new_slice=snippet, detail=f'patched lines {start_line}-{end_line}')


class TempRepo(AbstractContextManager):

    def __init__(self, repo_root: Path | str, *, keep: bool = False) -> None:
        self._source = Path(repo_root)
        self._keep = keep
        self._path: Path | None = None

    def __enter__(self) -> Path:
        self._path = copy_repo_to_temp(self._source)
        return self._path

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._path is None or self._keep:
            return
        parent = self._path.parent
        try:
            shutil.rmtree(parent, ignore_errors=True)
        except OSError as err:
            log.warning('Failed to clean temp dir %s: %s', parent, err)

    @property
    def path(self) -> Path | None:
        return self._path
