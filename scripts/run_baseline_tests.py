from __future__ import annotations
import os
import subprocess
from scripts.run_single_pass import _load_venv_manifest, _parse_pytest_output
import argparse
import json
import random
import sqlite3
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.test_selector import select_tests
from src.repo_patcher import copy_repo_to_temp
from src.config import DB_PATH
SEED = 42
OUT = ROOT / 'results' / 'analysis' / 'baseline_check.md'


def run_baseline_one(entry: dict, manifest: dict) -> dict:
    repo = entry['repo']
    repo_root = ROOT / 'data' / 'repos' / repo
    venv_info = manifest.get(repo, {})
    py = venv_info.get('python') or sys.executable
    layout = venv_info.get('pythonpath_layout') or ''
    temp_repo = copy_repo_to_temp(str(repo_root))
    try:
        parts = Path(entry['file_path']).parts
        i = parts.index(repo)
        target_file = temp_repo / Path(*parts[i + 1:])
        sel = select_tests(
            temp_repo,
            target_file,
            entry['function_name'],
            start_line=entry['start_line'],
            end_line=entry['end_line'],
            repo_name=repo)
        if sel.is_empty:
            return {'sample_id': entry['sample_id'], 'repo': repo, 'method': sel.method,
                    'passed': 0, 'failed': 0, 'errors': 0, 'note': 'no tests selected'}
        cmd = [
            py,
            '-m',
            'pytest',
            '-x',
            '-q',
            '--tb=no',
            '--no-header',
            '-p',
            'no:cacheprovider',
            *sel.nodeids]
        env = dict(os.environ)
        src_path = str(temp_repo / layout) if layout else str(temp_repo)
        env['PYTHONPATH'] = src_path + os.pathsep + env.get('PYTHONPATH', '')
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(temp_repo),
                capture_output=True,
                text=True,
                timeout=180,
                env=env)
            out = (proc.stdout or '') + '\n' + (proc.stderr or '')
            passed, failed, errors = _parse_pytest_output(out)
            return {'sample_id': entry['sample_id'], 'repo': repo, 'method': sel.method, 'passed': passed,
                    'failed': failed, 'errors': errors, 'dur': round(time.perf_counter() - t0, 1), 'note': ''}
        except subprocess.TimeoutExpired:
            return {'sample_id': entry['sample_id'], 'repo': repo, 'method': sel.method,
                    'passed': 0, 'failed': 0, 'errors': 0, 'note': 'TIMEOUT'}
    finally:
        import shutil
        shutil.rmtree(temp_repo, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-repo', type=int, default=7)
    args = ap.parse_args()
    index = json.loads((ROOT / 'data' / 'snapshots' / 'index.json').read_text(encoding='utf-8'))
    manifest = _load_venv_manifest()
    rng = random.Random(SEED)
    chosen: list[dict] = []
    for repo in ('requests', 'flask', 'httpie'):
        pool = [e for e in index if e['repo'] == repo]
        chosen += rng.sample(pool, min(args.per_repo, len(pool)))
    con = sqlite3.connect(str(DB_PATH))
    t_rows = {r[0]: (r[1] or 0, (r[2] or 0) + (r[3] or 0)) for r in con.execute(
        "SELECT sample_id, tests_passed, tests_failed, tests_errors\n               FROM experiment_results_v2 WHERE phase='4C' AND condition='T'")}
    lines = [
        '# Bezposredni pomiar linii bazowej testow (Etap 7.2)',
        '',
        f'Probka: {len(chosen)} migawek (po {args.per_repo}/repo, seed {SEED});',
        'identyczna selekcja testow i konfiguracja pytest (-x) jak w potoku 4C,',
        'lecz kod NIEZMODYFIKOWANY.',
        '',
        '| sample_id | repo | metoda | passed | failed+err (baseline) | failed+err (warunek T) | zgodne? |',
        '|---|---|---|---|---|---|---|']
    agree = total = 0
    for e in sorted(chosen, key=lambda x: x['sample_id']):
        r = run_baseline_one(e, manifest)
        fb = r['failed'] + r['errors']
        t_p, t_f = t_rows.get(r['sample_id'], (None, None))
        same = t_f is not None and fb == t_f
        total += 1
        agree += int(bool(same))
        mark = 'tak' if same else 'brak T' if t_f is None else 'NIE'
        lines.append(
            f"| {r['sample_id']} | {r['repo']} | {r['method']} | {r['passed']} | {fb} | {(t_f if t_f is not None else '-')} | {mark} {r['note']} |")
        print(f"{r['sample_id']}: baseline failed+err={fb}, T={t_f}, zgodne={mark} {r['note']}")
    lines += ['', f'Zgodnosc baseline vs warunek T: {agree}/{total} migawek.']
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'OK -> {OUT}')


if __name__ == '__main__':
    main()
