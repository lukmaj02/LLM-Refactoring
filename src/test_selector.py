from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestSelection:
    nodeids: list[str] = field(default_factory=list)
    method: str = 'none'
    detail: str = ''

    @property
    def is_empty(self) -> bool:
        return not self.nodeids


def _strip_class(function_name: str) -> str:
    return function_name.rsplit('.', 1)[-1]


def _module_dotted_path(repo_root: Path, file_path: Path) -> str | None:
    try:
        rel = file_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return None
    parts = list(rel.with_suffix('').parts)
    if parts and parts[0] == 'src':
        parts = parts[1:]
    if parts and parts[-1] == '__init__':
        parts = parts[:-1]
    return '.'.join(parts) if parts else None


def _load_coverage_map(repo_name: str) -> dict | None:
    candidate = Path('data/results') / f'{repo_name}_coverage.json'
    if not candidate.is_file():
        return None
    try:
        with candidate.open('r', encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _try_coverage_map(repo_name: str, file_path: str, start_line: int, end_line: int) -> list[str]:
    coverage = _load_coverage_map(repo_name)
    if not coverage:
        return []
    nodeids: set[str] = set()
    normalised = file_path.replace('\\', '/')
    for line in range(start_line, end_line + 1):
        key = f'{normalised}::{line}'
        for nid in coverage.get(key, []) or []:
            nodeids.add(nid)
    return sorted(nodeids)


_IDENT = re.compile('[A-Za-z_][A-Za-z0-9_]*')


def _try_grep_imports(tests_dir: Path, function_name: str, module_dotted: str | None) -> list[str]:
    if not tests_dir.is_dir():
        return []
    bare_name = _strip_class(function_name)
    if not _IDENT.fullmatch(bare_name):
        return []
    name_pattern = re.compile(f'\\b{re.escape(bare_name)}\\b')
    module_pattern = re.compile(f'\\b{re.escape(module_dotted)}\\b') if module_dotted else None
    matches: list[str] = []
    for test_file in tests_dir.rglob('test_*.py'):
        try:
            text = test_file.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue
        hit = bool(name_pattern.search(text))
        if not hit and module_pattern is not None:
            hit = bool(module_pattern.search(text))
        if hit:
            matches.append(str(test_file).replace('\\', '/'))
    return matches


def _module_fallback(tests_dir: Path, source_file: Path) -> list[str]:
    if not tests_dir.is_dir():
        return []
    basename = source_file.stem
    candidates = [tests_dir / f'test_{basename}.py', tests_dir / basename / f'test_{basename}.py']
    for cand in candidates:
        if cand.is_file():
            return [str(cand).replace('\\', '/')]
    return []


def select_tests(repo_root: Path | str, file_path: Path | str, function_name: str, *,
                 start_line: int = 0, end_line: int = 0, repo_name: str | None = None) -> TestSelection:
    repo_root = Path(repo_root)
    src_path = Path(file_path)
    if not src_path.is_absolute() and (not src_path.exists()):
        candidate = repo_root / src_path.name
        if candidate.exists():
            src_path = candidate
    repo_name = repo_name or repo_root.name
    coverage_hits = _try_coverage_map(repo_name, str(file_path), start_line, end_line)
    if coverage_hits:
        return TestSelection(nodeids=coverage_hits, method='coverage_map',
                             detail=f'{len(coverage_hits)} tests from coverage map')
    tests_dir = repo_root / 'tests'
    module_dotted = _module_dotted_path(repo_root, src_path)
    grep_hits = _try_grep_imports(tests_dir, function_name, module_dotted)
    if grep_hits:
        return TestSelection(nodeids=grep_hits, method='grep_import',
                             detail=f'{len(grep_hits)} test files reference {function_name}')
    module_hits = _module_fallback(tests_dir, src_path)
    if module_hits:
        return TestSelection(nodeids=module_hits, method='module_fallback',
                             detail=f'matched test_<{src_path.stem}>.py')
    if tests_dir.is_dir():
        return TestSelection(nodeids=[str(tests_dir).replace(
            '\\', '/')], method='tests_dir_fallback', detail='no targeted match; using full tests/ directory')
    return TestSelection(nodeids=[], method='none', detail='no tests/ dir')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Targeted pytest selector')
    parser.add_argument('repo_root')
    parser.add_argument('file_path')
    parser.add_argument('function_name')
    parser.add_argument('--start-line', type=int, default=0)
    parser.add_argument('--end-line', type=int, default=0)
    args = parser.parse_args()
    sel = select_tests(
        args.repo_root,
        args.file_path,
        args.function_name,
        start_line=args.start_line,
        end_line=args.end_line)
    print(f'method: {sel.method}')
    print(f'detail: {sel.detail}')
    print(f'nodeids ({len(sel.nodeids)}):')
    for nid in sel.nodeids[:20]:
        print(f'  {nid}')
