from __future__ import annotations
from scripts.run_single_pass import _load_venv_manifest, _parse_pytest_output
import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.test_selector import select_tests
from src.repo_patcher import copy_repo_to_temp, patch_function_in_file
from src.config import DB_PATH
DESELECT = [
    'tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_tls_settings_verify_bundle_unexpired_cert',
    'tests/test_requests.py::TestPreparingURLs::test_different_connection_pool_for_mtls_settings',
    'tests/test_httpie_cli.py::test_httpie_sessions_upgrade_on_non_existent_file']
SCHEMA = '\nCREATE TABLE IF NOT EXISTS test_gate_rerun (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    sample_id TEXT NOT NULL,\n    condition TEXT NOT NULL,          -- BASE / T / A / G / C\n    selection_method TEXT,\n    n_selected INTEGER,\n    passed INTEGER,\n    failed INTEGER,\n    errors INTEGER,\n    timeout INTEGER DEFAULT 0,\n    patch_ok INTEGER DEFAULT 1,\n    failed_ids TEXT,\n    duration_s REAL,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,\n    UNIQUE(sample_id, condition)\n);\n'


def run_one(entry: dict, condition: str, code: str | None, manifest: dict) -> dict:
    repo = entry['repo']
    venv = manifest.get(repo, {})
    py = venv.get('python') or sys.executable
    layout = venv.get('pythonpath_layout') or ''
    temp = copy_repo_to_temp(str(ROOT / 'data' / 'repos' / repo))
    try:
        parts = Path(entry['file_path']).parts
        i = parts.index(repo)
        target = temp / Path(*parts[i + 1:])
        if code is not None:
            patch = patch_function_in_file(target, code, entry['start_line'], entry['end_line'])
            if not patch.success:
                return {'patch_ok': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'timeout': 0,
                        'failed_ids': patch.detail[:400], 'method': 'n/a', 'n_sel': 0, 'dur': 0.0}
        sel = select_tests(
            temp,
            target,
            entry['function_name'],
            start_line=entry['start_line'],
            end_line=entry['end_line'],
            repo_name=repo)
        if sel.is_empty:
            return {'patch_ok': 1, 'passed': 0, 'failed': 0, 'errors': 0, 'timeout': 0,
                    'failed_ids': '', 'method': sel.method, 'n_sel': 0, 'dur': 0.0}
        cmd = [py, '-m', 'pytest', '-q', '--tb=no', '-rf', '--no-header', '-p', 'no:cacheprovider']
        for d in DESELECT:
            cmd += ['--deselect', d]
        cmd += sel.nodeids
        env = dict(os.environ)
        src = str(temp / layout) if layout else str(temp)
        env['PYTHONPATH'] = src + os.pathsep + env.get('PYTHONPATH', '')
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(temp),
                capture_output=True,
                text=True,
                timeout=420,
                env=env)
        except subprocess.TimeoutExpired:
            return {'patch_ok': 1, 'passed': 0, 'failed': 0, 'errors': 0, 'timeout': 1,
                    'failed_ids': '', 'method': sel.method, 'n_sel': len(sel.nodeids), 'dur': 420.0}
        dur = time.perf_counter() - t0
        out = (proc.stdout or '') + '\n' + (proc.stderr or '')
        passed, failed, errors = _parse_pytest_output(out)
        ids = ';'.join(re.findall('^FAILED (\\S+)', out, re.MULTILINE))
        return {'patch_ok': 1, 'passed': passed, 'failed': failed, 'errors': errors, 'timeout': 0,
                'failed_ids': ids[:8000], 'method': sel.method, 'n_sel': len(sel.nodeids), 'dur': round(dur, 1)}
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', choices=('requests', 'flask', 'httpie'))
    ap.add_argument('--shard', default=None, help='podzial pracy, format r/n (np. 0/3, 1/3, 2/3)')
    args = ap.parse_args()
    index = json.loads((ROOT / 'data' / 'snapshots' / 'index.json').read_text(encoding='utf-8'))
    if args.repo:
        index = [e for e in index if e['repo'] == args.repo]
    if args.shard:
        r, n = (int(x) for x in args.shard.split('/'))
        index = [e for i, e in enumerate(index) if i % n == r]
    manifest = _load_venv_manifest()
    con = sqlite3.connect(str(DB_PATH), timeout=60)
    con.execute(SCHEMA)
    con.commit()
    done = {(r[0], r[1]) for r in con.execute('SELECT sample_id, condition FROM test_gate_rerun')}
    arts = {(r[0], r[1]): r[2] for r in con.execute(
        "SELECT sample_id, condition, refactored_code_path\n           FROM experiment_results_v2\n           WHERE phase='4C' AND refactored_code_path IS NOT NULL")}
    jobs: list[tuple[dict, str, str | None]] = []
    snap_dir = ROOT / 'data' / 'snapshots'
    for e in index:
        sid = e['sample_id']
        if (sid, 'BASE') not in done:
            jobs.append((e, 'BASE', None))
        for cond in ('T', 'A', 'G', 'C'):
            path = arts.get((sid, cond))
            if path and (sid, cond) not in done:
                p = Path(path)
                if not p.is_absolute():
                    p = ROOT / path
                jobs.append((e, cond, p.read_text(encoding='utf-8')))
    print(f'zadan do wykonania: {len(jobs)} (pominieto gotowe: {len(done)})')
    for k, (entry, cond, code) in enumerate(jobs, 1):
        r = run_one(entry, cond, code, manifest)
        con.execute(
            'INSERT OR IGNORE INTO test_gate_rerun\n               (sample_id, condition, selection_method, n_selected, passed,\n                failed, errors, timeout, patch_ok, failed_ids, duration_s)\n               VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (entry['sample_id'],
             cond,
             r['method'],
                r['n_sel'],
                r['passed'],
                r['failed'],
                r['errors'],
                r['timeout'],
                r['patch_ok'],
                r['failed_ids'],
                r['dur']))
        con.commit()
        print(f"[{k}/{len(jobs)}] {entry['sample_id']} x {cond}: passed={r['passed']} failed={r['failed']} err={r['errors']} ({r['dur']}s)")
    print('KONIEC')


if __name__ == '__main__':
    main()
