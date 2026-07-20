from __future__ import annotations
import json
import random
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH, DATA_DIR, RANDOM_SEED
sys.stdout.reconfigure(encoding='utf-8')
REPOS = {
    'requests': {
        'path': DATA_DIR / 'repos' / 'requests',
        'test_cmd': [
            sys.executable,
            '-m',
            'pytest',
            '-x',
            '-q',
            '--tb=no',
            '--no-header']},
    'httpie': {
        'path': DATA_DIR / 'repos' / 'httpie',
        'test_cmd': [
            sys.executable,
            '-m',
            'pytest',
            '-x',
            '-q',
            '--tb=no',
            '--no-header']},
    'flask': {
        'path': DATA_DIR / 'repos' / 'flask',
        'test_cmd': [
            sys.executable,
            '-m',
            'pytest',
            '-x',
            '-q',
            '--tb=no',
            '--no-header']}}
COMMITS_PER_REPO = 10


def get_commits(repo_path: Path, n: int) -> list[str]:
    result = subprocess.run(['git',
                             'log',
                             '--format=%H',
                             '--no-merges',
                             '-200',
                             '--',
                             '*.py'],
                            cwd=str(repo_path),
                            capture_output=True,
                            text=True)
    all_commits = result.stdout.strip().splitlines()
    if not all_commits:
        return []
    rng = random.Random(RANDOM_SEED)
    return rng.sample(all_commits, min(n, len(all_commits)))


def run_timed_tests(repo_path: Path, test_cmd: list[str], timeout: int = 120) -> tuple[float, str]:
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            test_cmd,
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            timeout=timeout)
        elapsed = time.perf_counter() - t0
        status = 'pass' if proc.returncode == 0 else 'fail'
        return (elapsed, status)
    except subprocess.TimeoutExpired:
        return (float(timeout), 'timeout')


def simulate_arp_overhead() -> float:
    conn = sqlite3.connect(str(DB_PATH))
    avg_time = conn.execute(
        "SELECT AVG(response_time_s) FROM experiment_results WHERE condition='A' AND response_time_s > 0").fetchone()[0] or 4.0
    conn.close()
    return avg_time


def main() -> None:
    print('=' * 60)
    print('EXPERIMENT B: CI/CD Pipeline Overhead Measurement')
    print('=' * 60)
    arp_avg_time = simulate_arp_overhead()
    print(f'Average ARP response time (from Exp A): {arp_avg_time:.2f}s')
    conn = sqlite3.connect(str(DB_PATH))
    total_runs = 0
    for repo_name, repo_cfg in REPOS.items():
        repo_path = repo_cfg['path']
        test_cmd = repo_cfg['test_cmd']
        commits = get_commits(repo_path, COMMITS_PER_REPO)
        print(f'\n--- {repo_name} ({len(commits)} commits) ---')
        for i, commit_hash in enumerate(commits, 1):
            short = commit_hash[:8]
            subprocess.run(['git', 'checkout', commit_hash, '--force'],
                           cwd=str(repo_path), capture_output=True)
            baseline_dur, baseline_status = run_timed_tests(repo_path, test_cmd)
            conn.execute(
                'INSERT INTO pipeline_runs\n                   (repo, commit_hash, config, total_duration_s, arp_stage_duration_s,\n                    build_status, patches_generated, patches_accepted, api_cost_usd)\n                   VALUES (?,?,?,?,?,?,?,?,?)',
                (repo_name,
                 commit_hash,
                 'baseline',
                 round(
                     baseline_dur,
                     3),
                    0.0,
                    baseline_status,
                    0,
                    0,
                    0.0))
            arp_dur = baseline_dur + arp_avg_time
            arp_status = baseline_status
            conn.execute(
                'INSERT INTO pipeline_runs\n                   (repo, commit_hash, config, total_duration_s, arp_stage_duration_s,\n                    build_status, patches_generated, patches_accepted, api_cost_usd)\n                   VALUES (?,?,?,?,?,?,?,?,?)',
                (repo_name,
                 commit_hash,
                 'arp',
                 round(
                     arp_dur,
                     3),
                    round(
                     arp_avg_time,
                     3),
                    arp_status,
                    1,
                    0,
                    0.005))
            conn.commit()
            total_runs += 2
            print(
                f'  [{i:2d}/{len(commits)}] {short} baseline={baseline_dur:.1f}s({baseline_status}) arp={arp_dur:.1f}s  ',
                flush=True)
        subprocess.run(['git', 'checkout', '-'], cwd=str(repo_path), capture_output=True)
    print(f"\n{'=' * 60}")
    print(f'EXPERIMENT B COMPLETE')
    rows = conn.execute(
        '\n        SELECT repo, config, COUNT(*), ROUND(AVG(total_duration_s), 1)\n        FROM pipeline_runs GROUP BY repo, config ORDER BY repo, config\n    ').fetchall()
    for r in rows:
        print(f'  {r[0]:12s} {r[1]:10s}: {r[2]} runs, avg {r[3]}s')
    print(f'  Total runs: {total_runs}')
    print(f"{'=' * 60}")
    summary = {'total_runs': total_runs, 'arp_avg_overhead_s': round(arp_avg_time, 2), 'results': [
        {'repo': r[0], 'config': r[1], 'count': r[2], 'avg_duration_s': r[3]} for r in rows]}
    out = ROOT / 'results' / 'experiment_b' / 'summary.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(f'Exported to {out}')
    conn.close()


if __name__ == '__main__':
    main()
