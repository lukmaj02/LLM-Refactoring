from __future__ import annotations
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from radon.complexity import cc_visit
from radon.metrics import mi_visit


@dataclass
class TestResult:
    passed: int
    total: int
    duration_s: float
    output: str = field(default='', repr=False)


@dataclass
class MutationResult:
    score: float
    killed: int
    total: int


@dataclass
class ValidationDecision:
    accepted: bool
    reason: str | None
    detail: str | None = None


def run_tests(repo_path: str | Path, *, timeout: int = 300) -> TestResult:
    repo = Path(repo_path)
    try:
        proc = subprocess.run([sys.executable,
                               '-m',
                               'pytest',
                               '-x',
                               '-q',
                               '--tb=no',
                               '--no-header'],
                              cwd=str(repo),
                              capture_output=True,
                              text=True,
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return TestResult(passed=0, total=0, duration_s=float(timeout), output='TIMEOUT')
    output = proc.stdout + proc.stderr
    passed, total = _parse_pytest_summary(output)
    return TestResult(passed=passed, total=total, duration_s=0.0, output=output)


def _parse_pytest_summary(output: str) -> tuple[int, int]:
    import re
    passed = 0
    failed = 0
    errors = 0
    m_passed = re.search('(\\d+) passed', output)
    m_failed = re.search('(\\d+) failed', output)
    m_error = re.search('(\\d+) error', output)
    if m_passed:
        passed = int(m_passed.group(1))
    if m_failed:
        failed = int(m_failed.group(1))
    if m_error:
        errors = int(m_error.group(1))
    total = passed + failed + errors
    return (passed, total)


def measure_metrics(code: str) -> dict:
    blocks = cc_visit(code)
    cc = max((b.complexity for b in blocks), default=0)
    avg_cc = sum((b.complexity for b in blocks)) / len(blocks) if blocks else 0
    mi = mi_visit(code, multi=True)
    loc = len([ln for ln in code.splitlines() if ln.strip()])
    return {'cc': cc, 'avg_cc': round(avg_cc, 2), 'mi': round(mi, 2), 'loc': loc}


def measure_metrics_from_file(file_path: str | Path) -> dict:
    code = Path(file_path).read_text(encoding='utf-8')
    return measure_metrics(code)


def validate_refactoring(before: dict, after: dict, test_result: TestResult) -> ValidationDecision:
    if test_result.total > 0 and test_result.passed < test_result.total:
        return ValidationDecision(accepted=False, reason='test_failure',
                                  detail=f'{test_result.total - test_result.passed}/{test_result.total} tests failed')
    cc_improved = after['cc'] < before['cc']
    mi_improved = after['mi'] > before['mi']
    if not (cc_improved or mi_improved):
        return ValidationDecision(accepted=False, reason='no_metric_improvement',
                                  detail=f"CC {before['cc']}->{after['cc']}, MI {before['mi']}->{after['mi']}")
    return ValidationDecision(accepted=True, reason=None, detail='all gates passed')
