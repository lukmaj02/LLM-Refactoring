from __future__ import annotations
import json
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
SNAPSHOTS_DIR = ROOT / 'data' / 'snapshots'
INDEX_PATH = SNAPSHOTS_DIR / 'index.json'


def measure_snapshot_metrics(snapshot_path: Path) -> dict:
    cc_result = subprocess.run(['radon', 'cc', str(snapshot_path),
                               '--json', '-s'], capture_output=True, text=True)
    cc_data = json.loads(cc_result.stdout) if cc_result.stdout.strip() else {}
    max_cc = 0
    for blocks in cc_data.values():
        for block in blocks:
            if block.get('type') in ('function', 'method'):
                max_cc = max(max_cc, block.get('complexity', 0))
    mi_result = subprocess.run(['radon', 'mi', str(snapshot_path),
                               '--json'], capture_output=True, text=True)
    mi_data = json.loads(mi_result.stdout) if mi_result.stdout.strip() else {}
    mi_val = None
    for val in mi_data.values():
        if isinstance(val, (int, float)):
            mi_val = round(val, 2)
    raw_result = subprocess.run(['radon', 'raw', str(snapshot_path),
                                '--json'], capture_output=True, text=True)
    raw_data = json.loads(raw_result.stdout) if raw_result.stdout.strip() else {}
    loc = 0
    for metrics in raw_data.values():
        loc = metrics.get('sloc', 0)
    return {'cc': max_cc, 'mi': mi_val, 'loc': loc}


def run_repo_tests(repo: str) -> dict:
    test_configs = {
        'requests': {
            'cwd': ROOT / 'data' / 'repos' / 'requests',
            'cmd': [
                'python',
                '-m',
                'pytest',
                'tests/',
                '-q',
                '--tb=no',
                '-p',
                'no:httpbin']},
        'httpie': {
            'cwd': ROOT / 'data' / 'repos' / 'httpie',
            'cmd': [
                'python',
                '-m',
                'pytest',
                'tests/',
                '-q',
                '--tb=no',
                '-p',
                'no:httpbin']},
        'flask': {
            'cwd': ROOT / 'data' / 'repos' / 'flask',
            'cmd': [
                'python',
                '-m',
                'pytest',
                'tests/',
                '-q',
                '--tb=no']}}
    config = test_configs[repo]
    result = subprocess.run(
        config['cmd'],
        capture_output=True,
        text=True,
        cwd=str(
            config['cwd']),
        timeout=600)
    output = result.stdout + result.stderr
    passed = 0
    total = 0
    for line in output.splitlines():
        line = line.strip()
        if 'passed' in line:
            import re
            m = re.search('(\\d+)\\s+passed', line)
            if m:
                passed = int(m.group(1))
            m_fail = re.search('(\\d+)\\s+failed', line)
            failed = int(m_fail.group(1)) if m_fail else 0
            m_err = re.search('(\\d+)\\s+error', line)
            errors = int(m_err.group(1)) if m_err else 0
            m_skip = re.search('(\\d+)\\s+skipped', line)
            skipped = int(m_skip.group(1)) if m_skip else 0
            total = passed + failed + errors
    return {'passed': passed, 'total': total}


def main() -> None:
    with open(INDEX_PATH) as f:
        index = json.load(f)
    print(f'[baseline] Measuring metrics for {len(index)} snapshots...')
    metrics = {}
    for entry in index:
        sid = entry['sample_id']
        snapshot_path = SNAPSHOTS_DIR / entry['snapshot_file']
        m = measure_snapshot_metrics(snapshot_path)
        metrics[sid] = m
    print(f'[baseline] Metrics measured for {len(metrics)} snapshots')
    repos = sorted(set((e['repo'] for e in index)))
    test_results = {}
    for repo in repos:
        print(f'[baseline] Running tests for {repo}...')
        test_results[repo] = run_repo_tests(repo)
        print(f"  -> passed={test_results[repo]['passed']}, total={test_results[repo]['total']}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    inserted = 0
    for entry in index:
        sid = entry['sample_id']
        repo = entry['repo']
        m = metrics[sid]
        tr = test_results[repo]
        cursor.execute(
            "\n            INSERT INTO experiment_results (\n                sample_id, repo, file_path, function_name, condition,\n                cc_before, mi_before, loc_before,\n                tests_passed_before, tests_total_before,\n                mutation_score_before,\n                patch_applied, patch_accepted\n            ) VALUES (?, ?, ?, ?, 'K', ?, ?, ?, ?, ?, NULL, 0, 0)\n        ",
            (sid,
             repo,
             entry['file_path'],
                entry['function_name'],
                m['cc'],
                m['mi'],
                m['loc'],
                tr['passed'],
                tr['total']))
        inserted += 1
    conn.commit()
    count = cursor.execute(
        "SELECT COUNT(*) FROM experiment_results WHERE condition='K'").fetchone()[0]
    null_cc = cursor.execute(
        "SELECT COUNT(*) FROM experiment_results WHERE condition='K' AND cc_before IS NULL").fetchone()[0]
    conn.close()
    print(f'\n[baseline] Inserted {inserted} rows (condition=K)')
    print(f'[baseline] Verification: {count} rows, {null_cc} with NULL cc_before')
    condition_k = []
    for entry in index:
        sid = entry['sample_id']
        m = metrics[sid]
        tr = test_results[entry['repo']]
        condition_k.append({'sample_id': sid,
                            'repo': entry['repo'],
                            'condition': 'K',
                            **m,
                            'tests_passed': tr['passed'],
                            'tests_total': tr['total']})
    out_path = ROOT / 'data' / 'results' / 'condition_K.json'
    with open(out_path, 'w') as f:
        json.dump(condition_k, f, indent=2)
    print(f'[baseline] JSON saved to {out_path}')


if __name__ == '__main__':
    main()
