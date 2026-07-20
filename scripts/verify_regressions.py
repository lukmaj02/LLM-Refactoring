from __future__ import annotations
from scripts.run_single_pass import _load_venv_manifest, _parse_pytest_output
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
from src.repo_patcher import copy_repo_to_temp, patch_function_in_file
from src.config import DB_PATH
SCHEMA = '\nCREATE TABLE IF NOT EXISTS regression_verdicts (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    sample_id TEXT NOT NULL,\n    condition TEXT NOT NULL,\n    flagged_tests TEXT,\n    n_flagged INTEGER,\n    fail_on_artifact INTEGER,\n    fail_on_base INTEGER,\n    verdict TEXT,\n    detail TEXT,\n    duration_s REAL,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,\n    UNIQUE(sample_id, condition)\n);\n'


def fset(s):
    ids = [x for x in (s or '').split(';') if x]
    if ids and '::' not in ids[-1]:
        ids = ids[:-1]
    return set(ids)


def run_targeted(entry: dict, code: str | None,
                 node_ids: list[str], manifest: dict) -> tuple[set[str], int]:
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
                return (set(node_ids), 0)
        cmd = [
            py,
            '-m',
            'pytest',
            '-q',
            '--tb=no',
            '-rf',
            '--no-header',
            '-p',
            'no:cacheprovider',
            *node_ids]
        env = dict(os.environ)
        src = str(temp / layout) if layout else str(temp)
        env['PYTHONPATH'] = src + os.pathsep + env.get('PYTHONPATH', '')
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(temp),
                capture_output=True,
                text=True,
                timeout=240,
                env=env)
        except subprocess.TimeoutExpired:
            return (set(node_ids), 1)
        out = (proc.stdout or '') + '\n' + (proc.stderr or '')
        fails = set(re.findall('^FAILED (\\S+)', out, re.MULTILINE))
        errors = set(re.findall('^ERROR (\\S+)', out, re.MULTILINE))
        return (fails | errors, 0)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def main() -> None:
    con = sqlite3.connect(str(DB_PATH), timeout=60)
    con.execute(SCHEMA)
    con.commit()
    rr = {(r[0], r[1]): (r[2] or '', r[3], r[4]) for r in con.execute(
        'SELECT sample_id, condition, failed_ids, timeout, patch_ok FROM test_gate_rerun')}
    flagged: list[tuple[str, str, list[str]]] = []
    for (sid, cond), (ids, tmo, pok) in sorted(rr.items()):
        if cond == 'BASE' or pok == 0:
            continue
        b = rr.get((sid, 'BASE'))
        if b is None:
            continue
        new_fail = sorted(fset(ids) - fset(b[0]))
        if tmo == 1:
            new_fail = ['TIMEOUT_FULL_RUN']
        if new_fail:
            flagged.append((sid, cond, new_fail))
    print(f'oflagowanych par: {len(flagged)}')
    done = {(r[0], r[1])
            for r in con.execute('SELECT sample_id, condition FROM regression_verdicts')}
    index = {
        e['sample_id']: e for e in json.loads(
            (ROOT /
             'data' /
             'snapshots' /
             'index.json').read_text(
                encoding='utf-8'))}
    manifest = _load_venv_manifest()
    arts = {(r[0], r[1]): r[2] for r in con.execute(
        "SELECT sample_id, condition, refactored_code_path\n           FROM experiment_results_v2\n           WHERE phase='4C' AND refactored_code_path IS NOT NULL")}
    for k, (sid, cond, tests) in enumerate(flagged, 1):
        if (sid, cond) in done:
            continue
        entry = index[sid]
        t0 = time.perf_counter()
        if tests == ['TIMEOUT_FULL_RUN']:
            verdict, f_art, f_base, detail = ('timeout_full_run', -1, -1, '')
        else:
            p = Path(arts[sid, cond])
            if not p.is_absolute():
                p = ROOT / arts[sid, cond]
            code = p.read_text(encoding='utf-8')
            art_fail, tmo_a = run_targeted(entry, code, tests, manifest)
            base_fail, tmo_b = run_targeted(entry, None, tests, manifest)
            f_art, f_base = (len(art_fail), len(base_fail))
            really_new = art_fail - base_fail
            if tmo_a or tmo_b:
                verdict = 'timeout_targeted'
            elif really_new:
                verdict = 'confirmed'
            elif f_base > 0:
                verdict = 'env_unstable'
            else:
                verdict = 'not_reproduced'
            detail = ';'.join(sorted(really_new))[:2000]
        dur = round(time.perf_counter() - t0, 1)
        con.execute(
            'INSERT OR IGNORE INTO regression_verdicts\n               (sample_id, condition, flagged_tests, n_flagged,\n                fail_on_artifact, fail_on_base, verdict, detail, duration_s)\n               VALUES (?,?,?,?,?,?,?,?,?)',
            (sid,
             cond,
             ';'.join(tests)[
                 :4000],
                len(tests),
                f_art,
                f_base,
                verdict,
                detail,
                dur))
        con.commit()
        print(f'[{k}/{len(flagged)}] {sid} x {cond}: {verdict} (art={f_art}, base={f_base}, {dur}s)')
    print('KONIEC')


if __name__ == '__main__':
    main()
