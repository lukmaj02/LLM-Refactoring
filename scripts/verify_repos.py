from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import RANDOM_SEED
REPOS = {
    'requests': {
        'source_dir': ROOT / 'data' / 'repos' / 'requests' / 'src' / 'requests',
        'cc_raw': ROOT / 'data' / 'results' / 'requests_cc_raw.json',
        'mi_raw': ROOT / 'data' / 'results' / 'requests_mi_raw.json',
        'repo_root': ROOT / 'data' / 'repos' / 'requests'},
    'httpie': {
        'source_dir': ROOT / 'data' / 'repos' / 'httpie' / 'httpie',
        'cc_raw': ROOT / 'data' / 'results' / 'httpie_cc_raw.json',
        'mi_raw': ROOT / 'data' / 'results' / 'httpie_mi_raw.json',
        'repo_root': ROOT / 'data' / 'repos' / 'httpie'},
    'flask': {
        'source_dir': ROOT / 'data' / 'repos' / 'flask' / 'src' / 'flask',
        'cc_raw': ROOT / 'data' / 'results' / 'flask_cc_raw.json',
        'mi_raw': ROOT / 'data' / 'results' / 'flask_mi_raw.json',
        'repo_root': ROOT / 'data' / 'repos' / 'flask'}}
THRESHOLDS = {'coverage_pct': 60, 'functions_cc_ge_5': 30}


def count_loc(source_dir: Path) -> dict:
    result = subprocess.run(['radon', 'raw', str(source_dir), '--json'],
                            capture_output=True, text=True)
    data = json.loads(result.stdout)
    total = 0
    source = 0
    for file_metrics in data.values():
        total += file_metrics.get('loc', 0)
        source += file_metrics.get('sloc', 0)
    return {'loc_total': total, 'loc_source': source}


def analyse_cc(cc_raw_path: Path) -> dict:
    with open(cc_raw_path) as f:
        data = json.load(f)
    functions_total = 0
    functions_cc_ge_5 = 0
    functions_cc_ge_10 = 0
    cc_sum = 0
    for file_blocks in data.values():
        for block in file_blocks:
            if block.get('type') in ('function', 'method'):
                cc = block.get('complexity', 0)
                functions_total += 1
                cc_sum += cc
                if cc >= 5:
                    functions_cc_ge_5 += 1
                if cc >= 10:
                    functions_cc_ge_10 += 1
    avg_cc = round(cc_sum / functions_total, 2) if functions_total > 0 else 0
    return {'functions_total': functions_total, 'functions_cc_ge_5': functions_cc_ge_5,
            'functions_cc_ge_10': functions_cc_ge_10, 'avg_cc': avg_cc}


def check_ci(repo_root: Path) -> bool:
    return (repo_root / '.github' / 'workflows').is_dir()


def build_report() -> dict:
    report: dict = {
        'generated_at': datetime.now(
            timezone.utc).isoformat(),
        'seed': RANDOM_SEED,
        'repos': {}}
    for name, paths in REPOS.items():
        print(f'[verify] Processing {name} ...')
        loc_info = count_loc(paths['source_dir'])
        cc_info = analyse_cc(paths['cc_raw'])
        ci_present = check_ci(paths['repo_root'])
        coverage_pct = -1
        threshold_failures = []
        if coverage_pct >= 0 and coverage_pct < THRESHOLDS['coverage_pct']:
            threshold_failures.append(f"coverage_pct={coverage_pct} < {THRESHOLDS['coverage_pct']}")
        if cc_info['functions_cc_ge_5'] < THRESHOLDS['functions_cc_ge_5']:
            threshold_failures.append(
                f"functions_cc_ge_5={cc_info['functions_cc_ge_5']} < {THRESHOLDS['functions_cc_ge_5']}")
        if not ci_present:
            threshold_failures.append('ci_cd_present=false')
        passes = len(threshold_failures) == 0
        report['repos'][name] = {
            **loc_info,
            'coverage_pct': coverage_pct,
            **cc_info,
            'ci_cd_present': ci_present,
            'passes_thresholds': passes,
            'threshold_failures': threshold_failures}
        print(f"  LOC={loc_info['loc_total']}  SLOC={loc_info['loc_source']}  CC>=5: {cc_info['functions_cc_ge_5']}  CC>=10: {cc_info['functions_cc_ge_10']}  CI: {ci_present}  PASS: {passes}")
    return report


def main() -> None:
    report = build_report()
    out_path = ROOT / 'data' / 'repo_verification_report.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f'\n[verify] Report written to {out_path}')


if __name__ == '__main__':
    main()
