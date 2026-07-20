from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
COVERAGE_FILES = {'requests': ROOT / 'data' / 'results' / 'requests_coverage.json',
                  'httpie': ROOT / 'data' / 'results' / 'httpie_coverage.json',
                  'flask': ROOT / 'data' / 'results' / 'flask_coverage.json'}
REPORT_PATH = ROOT / 'data' / 'repo_verification_report.json'
COVERAGE_THRESHOLD = 60


def main() -> None:
    with open(REPORT_PATH) as f:
        report = json.load(f)
    for name, cov_path in COVERAGE_FILES.items():
        if not cov_path.exists():
            print(f'[warn] Missing coverage file for {name}')
            continue
        with open(cov_path) as f:
            cov = json.load(f)
        pct = round(cov['totals']['percent_covered'], 1)
        report['repos'][name]['coverage_pct'] = pct
        failures = report['repos'][name]['threshold_failures']
        failures = [f for f in failures if not f.startswith('coverage_pct')]
        if pct < COVERAGE_THRESHOLD:
            failures.append(f'coverage_pct={pct} < {COVERAGE_THRESHOLD}')
        report['repos'][name]['threshold_failures'] = failures
        report['repos'][name]['passes_thresholds'] = len(failures) == 0
        print(f"[update] {name}: coverage={pct}%  passes={report['repos'][name]['passes_thresholds']}")
    with open(REPORT_PATH, 'w') as f:
        json.dump(report, f, indent=2)
    print(f'\n[update] Report updated: {REPORT_PATH}')


if __name__ == '__main__':
    main()
