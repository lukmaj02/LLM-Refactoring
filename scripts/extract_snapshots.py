from __future__ import annotations
import ast
import json
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def resolve_source_path(repo: str, file_path: str) -> Path:
    return ROOT / file_path


def extract_function_source(file_path: Path, func_name: str,
                            start_line: int, end_line: int) -> str | None:
    try:
        source = file_path.read_text(encoding='utf-8')
    except (FileNotFoundError, UnicodeDecodeError):
        return None
    lines = source.splitlines(keepends=True)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        extracted = lines[start_line - 1:end_line]
        return ''.join(extracted)
    target_name = func_name.split('.')[-1]
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name == target_name and node.lineno == start_line:
                node_end = node.end_lineno or end_line
                extracted = lines[node.lineno - 1:node_end]
                return ''.join(extracted)
    extracted = lines[start_line - 1:end_line]
    return ''.join(extracted)


def make_snapshot_header(sample: dict) -> str:
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    mi_str = f"{sample['mi']}" if sample.get('mi') is not None else 'N/A'
    return f"# SNAPSHOT METADATA\n# sample_id: {sample['sample_id']}\n# repo: {sample['repo']}\n# file: {sample['file_path']}\n# function: {sample['function_name']}\n# cc: {sample['cc']} | mi: {mi_str} | loc: {sample['loc']}\n# extracted: {ts}\n\n"


def main() -> None:
    samples_path = ROOT / 'data' / 'samples' / 'functions_sample.json'
    with open(samples_path) as f:
        samples = json.load(f)
    snapshots_dir = ROOT / 'data' / 'snapshots'
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    index = []
    success = 0
    failed = 0
    for sample in samples:
        sid = sample['sample_id']
        repo = sample['repo']
        file_path = sample['file_path']
        func_name = sample['function_name']
        start_line = sample['start_line']
        end_line = sample['end_line']
        src_path = resolve_source_path(repo, file_path)
        code = extract_function_source(src_path, func_name, start_line, end_line)
        if code is None:
            print(f'[WARN] Failed to extract {sid}: {file_path}:{func_name}')
            failed += 1
            continue
        code_dedented = textwrap.dedent(code)
        header = make_snapshot_header(sample)
        snapshot_path = snapshots_dir / f'{sid}.py'
        snapshot_path.write_text(header + code_dedented, encoding='utf-8')
        try:
            ast.parse(code_dedented)
            valid = True
        except SyntaxError:
            valid = False
            print(f'[WARN] Syntax error in {sid} — keeping file but flagging')
        index.append({'sample_id': sid, 'snapshot_file': f'{sid}.py',
                     'syntax_valid': valid, **sample})
        success += 1
    index_path = snapshots_dir / 'index.json'
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    print(f'\n[extract] Done: {success} extracted, {failed} failed')
    print(f'[extract] Index written to {index_path}')


if __name__ == '__main__':
    main()
