from __future__ import annotations
import threading
import argparse
import ast
import hashlib
import json
import logging
import re
import sqlite3
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.validator import measure_metrics
from src.test_selector import select_tests
from src.repo_patcher import copy_repo_to_temp, patch_function_in_file
from src.quality_validator import QualityValidator
from src.prompts import build_prompt_with_context
from src.patch_generator import strip_markdown_fences
from src.config import DB_PATH, MODELS
from src.ai_client import AIClient
log = logging.getLogger('faza4c')
SNAPSHOTS_DIR = ROOT / 'data' / 'snapshots'
REPOS_DIR = ROOT / 'data' / 'repos'
REFACTORED_DIR = ROOT / 'data' / 'refactored_v2'
LOGS_DIR = ROOT / 'logs' / 'faza_4c'
VENVS_MANIFEST = ROOT / 'data' / 'venvs' / 'manifest.json'


def _load_venv_manifest() -> dict[str, dict[str, str]]:
    if not VENVS_MANIFEST.is_file():
        log.warning(
            'Venvs manifest missing at %s - falling back to system Python. Run scripts/setup_repo_venvs.py first for reliable tests.',
            VENVS_MANIFEST)
        return {}
    with VENVS_MANIFEST.open('r', encoding='utf-8') as fh:
        return json.load(fh)


CONDITIONS_AI = ('A', 'G', 'C')
CONDITION_TRADITIONAL = 'T'
ALL_CONDITIONS = (CONDITION_TRADITIONAL,) + CONDITIONS_AI


@dataclass
class TestRunResult:
    targeted: int = 0
    run: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    timeout: int = 0
    duration_s: float = 0.0
    selection_method: str = 'none'
    nodeids: list[str] = field(default_factory=list)
    raw_output: str = ''


def _setup_logging(verbose: bool) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(
                sys.stdout),
            logging.FileHandler(
                LOGS_DIR /
                f'orchestrator_{datetime.now():%Y%m%dT%H%M%S}.log',
                encoding='utf-8')])


def _load_index() -> list[dict[str, Any]]:
    with (SNAPSHOTS_DIR / 'index.json').open('r', encoding='utf-8') as fh:
        return json.load(fh)


def _read_snapshot(sample_id: str) -> str:
    raw = (SNAPSHOTS_DIR / f'{sample_id}.py').read_text(encoding='utf-8')
    lines = raw.splitlines(keepends=True)
    body_start = 0
    for i, ln in enumerate(lines):
        if ln.startswith('#'):
            body_start = i + 1
            continue
        if ln.strip() == '':
            body_start = i + 1
            continue
        break
    return ''.join(lines[body_start:])


def _read_full_file(repo: str, file_path: str) -> str:
    abs_path = ROOT / file_path
    if not abs_path.is_file():
        abs_path = REPOS_DIR / repo / Path(file_path).name
    return abs_path.read_text(encoding='utf-8', errors='replace')


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _existing_keys(conn: sqlite3.Connection) -> set[tuple[str, str]]:
    rows = conn.execute(
        "SELECT sample_id, condition FROM experiment_results_v2 WHERE phase='4C'").fetchall()
    return {(r[0], r[1]) for r in rows}


def _write_refactored_file(sample_id: str, condition: str, code: str,
                           sample: dict[str, Any], changed_pct: float) -> Path:
    REFACTORED_DIR.mkdir(parents=True, exist_ok=True)
    header = f"# === ARP Faza 4C - refactored code ===\n# sample_id: {sample_id}\n# condition: {condition}\n# timestamp: {datetime.now().isoformat(timespec='seconds')}\n# original_cc: {sample.get('cc')}, original_mi: {sample.get('mi')}\n# changed_pct: {changed_pct:.4f}\n# === END HEADER ===\n"
    path = REFACTORED_DIR / f'{sample_id}_{condition}.py'
    path.write_text(header + code, encoding='utf-8')
    return path


def _apply_traditional(code: str) -> str:
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        tmp = Path(f.name)
    try:
        subprocess.run([sys.executable, '-m', 'autopep8', '--in-place', '--aggressive',
                       '--aggressive', str(tmp)], capture_output=True, timeout=30)
        subprocess.run([sys.executable, '-m', 'autoflake', '--in-place',
                       '--remove-all-unused-imports', str(tmp)], capture_output=True, timeout=30)
        return tmp.read_text(encoding='utf-8')
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


@dataclass
class RefactorResult:
    refactored_code: str
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0.0
    response_time_s: float = 0.0
    refused: bool = False
    model_name: str = ''
    error: str | None = None


def _call_model(sample: dict[str, Any], original_code: str, full_file: str,
                condition: str, client: AIClient) -> RefactorResult:
    if condition == CONDITION_TRADITIONAL:
        t0 = time.perf_counter()
        try:
            refactored = _apply_traditional(original_code)
        except (subprocess.TimeoutExpired, OSError) as exc:
            return RefactorResult(refactored_code=original_code,
                                  error=f'traditional_failed: {exc}', model_name='autopep8+autoflake')
        return RefactorResult(refactored_code=refactored, response_time_s=round(
            time.perf_counter() - t0, 3), model_name='autopep8+autoflake')
    model_cfg = MODELS[condition]
    messages = build_prompt_with_context(
        sample_meta={
            'file_path': sample['file_path'],
            'function_name': sample['function_name'],
            'cc': sample.get('cc'),
            'mi': sample.get('mi'),
            'start_line': sample.get('start_line'),
            'end_line': sample.get('end_line')},
        code_block=original_code,
        full_file_content=full_file,
        use_few_shot=True)
    try:
        resp = client.complete(messages, model_cfg, temperature=0.0)
    except Exception as exc:
        return RefactorResult(refactored_code=original_code,
                              error=f'llm_failed: {exc}', model_name=model_cfg['name'])
    return RefactorResult(refactored_code=strip_markdown_fences(resp.content), tokens_in=resp.tokens_in, tokens_out=resp.tokens_out,
                          cost_usd=resp.cost_usd, response_time_s=resp.response_time_s, refused=resp.refused, model_name=resp.model)


_PYTEST_SUMMARY = re.compile(
    '(?:(?P<failed>\\d+) failed)?[, ]*(?:(?P<passed>\\d+) passed)?[, ]*(?:(?P<errors>\\d+) error[s]?)?')


def _parse_pytest_output(output: str) -> tuple[int, int, int]:
    passed = failed = errors = 0
    for m in re.finditer('(\\d+) passed', output):
        passed = int(m.group(1))
    for m in re.finditer('(\\d+) failed', output):
        failed = int(m.group(1))
    for m in re.finditer('(\\d+) error', output):
        errors = int(m.group(1))
    return (passed, failed, errors)


def _run_pytest_in_temp(repo_root: str, file_path: str, function_name: str, refactored_code: str, start_line: int, end_line: int,
                        repo_name: str, timeout_s: int = 180, venv_python: str | None = None, pythonpath_layout: str = '') -> dict[str, Any]:
    temp_repo: Path | None = None
    try:
        temp_repo = copy_repo_to_temp(repo_root)
        relative_path = Path(file_path)
        parts = relative_path.parts
        try:
            i = parts.index(repo_name)
            rel = Path(*parts[i + 1:])
        except ValueError:
            rel = relative_path
        target_file = temp_repo / rel
        patch = patch_function_in_file(target_file, refactored_code, start_line, end_line)
        if not patch.success:
            return {'ok': False, 'error': patch.detail, 'selection_method': 'n/a', 'nodeids': [],
                    'passed': 0, 'failed': 0, 'errors': 0, 'timeout': 0, 'duration_s': 0.0, 'output': patch.detail}
        sel = select_tests(
            temp_repo,
            target_file,
            function_name,
            start_line=start_line,
            end_line=end_line,
            repo_name=repo_name)
        if sel.is_empty:
            return {'ok': True, 'selection_method': sel.method, 'nodeids': [], 'passed': 0,
                    'failed': 0, 'errors': 0, 'timeout': 0, 'duration_s': 0.0, 'output': 'no tests selected'}
        py = venv_python or sys.executable
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
        env = dict(__import__('os').environ)
        src_path = str(temp_repo / pythonpath_layout) if pythonpath_layout else str(temp_repo)
        env['PYTHONPATH'] = src_path + __import__('os').pathsep + env.get('PYTHONPATH', '')
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        t0 = time.perf_counter()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(temp_repo),
                capture_output=True,
                text=True,
                timeout=timeout_s,
                env=env)
            elapsed = time.perf_counter() - t0
            output = (proc.stdout or '') + '\n' + (proc.stderr or '')
            passed, failed, errors = _parse_pytest_output(output)
            return {'ok': True, 'selection_method': sel.method, 'nodeids': sel.nodeids, 'passed': passed,
                    'failed': failed, 'errors': errors, 'timeout': 0, 'duration_s': round(elapsed, 2), 'output': output[-4000:]}
        except subprocess.TimeoutExpired:
            return {'ok': True, 'selection_method': sel.method, 'nodeids': sel.nodeids, 'passed': 0,
                    'failed': 0, 'errors': 0, 'timeout': 1, 'duration_s': float(timeout_s), 'output': 'TIMEOUT'}
    except Exception:
        return {'ok': False, 'error': traceback.format_exc(limit=3), 'selection_method': 'n/a', 'nodeids': [
        ], 'passed': 0, 'failed': 0, 'errors': 0, 'timeout': 0, 'duration_s': 0.0, 'output': ''}
    finally:
        if temp_repo is not None:
            import shutil
            shutil.rmtree(temp_repo.parent, ignore_errors=True)


_INSERT_SQL = '\nINSERT INTO experiment_results_v2 (\n    sample_id, repo, file_path, function_name, condition,\n    cc_before, mi_before, loc_before,\n    cc_after, mi_after, loc_after,\n    patch_applied, patch_accepted, rejection_reason, changed_pct,\n    model_name, tokens_in, tokens_out, cost_usd, response_time_s, refused,\n    audit_log_path,\n    refactored_code_path, refactored_code_hash, prompt_with_context, temperature,\n    tests_targeted, tests_run, tests_passed, tests_failed, tests_errors,\n    tests_timeout, tests_duration_s, tests_selection_method,\n    solid_score, dry_score, kiss_score, semantic_score, quality_score,\n    quality_rationale, judge_called_on_path, phase\n) VALUES (\n    :sample_id, :repo, :file_path, :function_name, :condition,\n    :cc_before, :mi_before, :loc_before,\n    :cc_after, :mi_after, :loc_after,\n    :patch_applied, :patch_accepted, :rejection_reason, :changed_pct,\n    :model_name, :tokens_in, :tokens_out, :cost_usd, :response_time_s, :refused,\n    :audit_log_path,\n    :refactored_code_path, :refactored_code_hash, :prompt_with_context, :temperature,\n    :tests_targeted, :tests_run, :tests_passed, :tests_failed, :tests_errors,\n    :tests_timeout, :tests_duration_s, :tests_selection_method,\n    :solid_score, :dry_score, :kiss_score, :semantic_score, :quality_score,\n    :quality_rationale, :judge_called_on_path, :phase\n)\n'


def _persist_row(conn: sqlite3.Connection,
                 row: dict[str, Any], lock: 'threading.Lock | None' = None) -> None:
    if lock is not None:
        with lock:
            conn.execute(_INSERT_SQL, row)
            conn.commit()
    else:
        conn.execute(_INSERT_SQL, row)
        conn.commit()


def _changed_pct(original: str, refactored: str) -> float:
    import difflib
    orig_lines = original.splitlines()
    ref_lines = refactored.splitlines()
    sm = difflib.SequenceMatcher(a=orig_lines, b=ref_lines, autojunk=False)
    total = max(len(orig_lines), len(ref_lines), 1)
    matched = sum((b.size for b in sm.get_matching_blocks()))
    return round(1.0 - matched / total, 4)


def run_one(sample: dict[str, Any], condition: str, client: AIClient, judge: QualityValidator, *, pytest_pool: ProcessPoolExecutor |
            None, pytest_timeout: int, venv_manifest: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    sample_id = sample['sample_id']
    repo = sample['repo']
    original_code = _read_snapshot(sample_id)
    try:
        full_file = _read_full_file(repo, sample['file_path'])
    except OSError as exc:
        full_file = original_code
        log.warning('Could not read full file for %s: %s', sample_id, exc)
    before_metrics = measure_metrics(original_code)
    rr = _call_model(sample, original_code, full_file, condition, client)
    refactored = rr.refactored_code
    rejection_reason: str | None = None
    patch_applied = 1
    try:
        ast.parse(refactored)
        after_metrics = measure_metrics(refactored)
    except SyntaxError as exc:
        rejection_reason = f'syntax_error: {exc.msg}'
        patch_applied = 0
        after_metrics = {'cc': None, 'mi': None, 'loc': None}
    if rr.error:
        rejection_reason = rejection_reason or rr.error
        patch_applied = 0
    changed_pct = _changed_pct(original_code, refactored)
    code_path = _write_refactored_file(sample_id, condition, refactored, sample, changed_pct)
    code_hash = _sha256(refactored)
    test = TestRunResult()
    if patch_applied == 1:
        repo_root = (REPOS_DIR / repo).as_posix()
        venv_info = (venv_manifest or {}).get(repo, {})
        venv_py = venv_info.get('python') or sys.executable
        layout = venv_info.get('pythonpath_layout') or ''
        fut_args = (repo_root, sample['file_path'], sample['function_name'], refactored, int(
            sample['start_line']), int(sample['end_line']), repo, pytest_timeout, venv_py, layout)
        if pytest_pool is not None:
            fut = pytest_pool.submit(_run_pytest_in_temp, *fut_args)
            tr = fut.result()
        else:
            tr = _run_pytest_in_temp(*fut_args)
        test.targeted = len(tr.get('nodeids') or [])
        test.run = test.targeted
        test.passed = int(tr.get('passed', 0))
        test.failed = int(tr.get('failed', 0))
        test.errors = int(tr.get('errors', 0))
        test.timeout = int(tr.get('timeout', 0))
        test.duration_s = float(tr.get('duration_s', 0.0))
        test.selection_method = tr.get('selection_method') or 'none'
        test.nodeids = tr.get('nodeids') or []
        test.raw_output = tr.get('output', '')
    quality: dict[str, Any] = {'solid': None, 'dry': None, 'kiss': None,
                               'semantic': None, 'overall': None, 'rationale': None, 'judge_path': None}
    if patch_applied == 1:
        try:
            saved_code = code_path.read_text(encoding='utf-8')
            split = saved_code.split('# === END HEADER ===\n', 1)
            judge_input = split[1] if len(split) == 2 else saved_code
            qs = judge.evaluate(original_code, judge_input)
            quality.update({'solid': qs.solid_score,
                            'dry': qs.dry_score,
                            'kiss': qs.kiss_score,
                            'semantic': qs.semantic_score,
                            'overall': qs.overall_score,
                            'rationale': qs.rationale,
                            'judge_path': str(code_path)})
        except Exception as exc:
            log.warning('Judge failed for %s/%s: %s', sample_id, condition, exc)
            quality['rationale'] = f'JUDGE_ERROR: {exc}'
    accepted = 0
    if patch_applied == 1 and after_metrics['cc'] is not None:
        tests_ok = test.targeted == 0 or (
            test.failed == 0 and test.errors == 0 and (
                test.timeout == 0) and (
                test.passed > 0))
        cc_improved = before_metrics['cc'] is not None and after_metrics['cc'] < before_metrics['cc']
        mi_improved = before_metrics['mi'] is not None and after_metrics['mi'] is not None and (
            after_metrics['mi'] > before_metrics['mi'])
        if tests_ok and (cc_improved or mi_improved):
            accepted = 1
        elif not tests_ok:
            rejection_reason = rejection_reason or 'test_failure'
        elif not (cc_improved or mi_improved):
            rejection_reason = rejection_reason or 'no_metric_improvement'
    audit_log_path = LOGS_DIR / f'audit_{sample_id}_{condition}.json'
    try:
        with audit_log_path.open('w', encoding='utf-8') as fh:
            json.dump({'sample_id': sample_id,
                       'condition': condition,
                       'model_name': rr.model_name,
                       'tokens_in': rr.tokens_in,
                       'tokens_out': rr.tokens_out,
                       'cost_usd': rr.cost_usd,
                       'response_time_s': rr.response_time_s,
                       'refused': rr.refused,
                       'changed_pct': changed_pct,
                       'rejection_reason': rejection_reason,
                       'tests': {'targeted': test.targeted,
                                 'passed': test.passed,
                                 'failed': test.failed,
                                 'errors': test.errors,
                                 'timeout': test.timeout,
                                 'duration_s': test.duration_s,
                                 'selection_method': test.selection_method,
                                 'output_tail': test.raw_output[-2000:]},
                       'quality': quality},
                      fh,
                      indent=2,
                      default=str)
    except OSError:
        pass
    return {'sample_id': sample_id, 'repo': repo, 'file_path': sample['file_path'], 'function_name': sample['function_name'], 'condition': condition, 'cc_before': before_metrics['cc'], 'mi_before': before_metrics['mi'], 'loc_before': before_metrics['loc'], 'cc_after': after_metrics['cc'], 'mi_after': after_metrics['mi'], 'loc_after': after_metrics['loc'], 'patch_applied': patch_applied, 'patch_accepted': accepted, 'rejection_reason': rejection_reason, 'changed_pct': changed_pct, 'model_name': rr.model_name, 'tokens_in': rr.tokens_in, 'tokens_out': rr.tokens_out, 'cost_usd': rr.cost_usd, 'response_time_s': rr.response_time_s, 'refused': int(rr.refused), 'audit_log_path': str(audit_log_path), 'refactored_code_path': str(
        code_path), 'refactored_code_hash': code_hash, 'prompt_with_context': 1 if condition != CONDITION_TRADITIONAL else 0, 'temperature': 0.0 if condition != CONDITION_TRADITIONAL else None, 'tests_targeted': test.targeted, 'tests_run': test.run, 'tests_passed': test.passed, 'tests_failed': test.failed, 'tests_errors': test.errors, 'tests_timeout': test.timeout, 'tests_duration_s': test.duration_s, 'tests_selection_method': test.selection_method, 'solid_score': quality['solid'], 'dry_score': quality['dry'], 'kiss_score': quality['kiss'], 'semantic_score': quality['semantic'], 'quality_score': quality['overall'], 'quality_rationale': quality['rationale'], 'judge_called_on_path': quality['judge_path'], 'phase': '4C'}


def run(sample_ids: list[str] | None, conditions: list[str], *, limit: int | None = None,
        skip_existing: bool = True, pytest_workers: int = 4, pytest_timeout: int = 180, serial_llm: bool = False) -> None:
    index = _load_index()
    if sample_ids:
        wanted = set(sample_ids)
        index = [s for s in index if s['sample_id'] in wanted]
    if limit:
        index = index[:limit]
    REFACTORED_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    import threading
    db_lock = threading.Lock()
    done = _existing_keys(conn) if skip_existing else set()
    client = AIClient(max_retries=4, base_delay=3.0)
    judge = QualityValidator(model_condition='G')
    venv_manifest = _load_venv_manifest()
    tasks: list[tuple[dict[str, Any], str]] = [
        (s, c) for s in index for c in conditions if (s['sample_id'], c) not in done]
    log.info('Planned %d (sample, condition) tasks', len(tasks))
    pool = ProcessPoolExecutor(max_workers=pytest_workers) if pytest_workers > 1 else None
    if serial_llm or len(tasks) <= 1:
        for sample, cond in tasks:
            _do_one(sample, cond, client, judge, conn, pool, pytest_timeout, venv_manifest, db_lock)
    else:
        with ThreadPoolExecutor(max_workers=len(set(conditions)) or 1) as tx:
            futures = {}
            by_condition: dict[str, list[dict[str, Any]]] = {}
            for sample, cond in tasks:
                by_condition.setdefault(cond, []).append(sample)

            def _worker(cond: str, samples: list[dict[str, Any]]) -> None:
                for sample in samples:
                    _do_one(
                        sample,
                        cond,
                        client,
                        judge,
                        conn,
                        pool,
                        pytest_timeout,
                        venv_manifest,
                        db_lock)
            for cond, samples in by_condition.items():
                futures[tx.submit(_worker, cond, samples)] = cond
            for fut in as_completed(futures):
                exc = fut.exception()
                if exc:
                    log.error('Worker for cond=%s failed: %s', futures[fut], exc)
    if pool is not None:
        pool.shutdown(wait=True)
    conn.close()
    log.info('Done. Total LLM cost: $%.4f', client.total_cost + judge.total_cost)


def _do_one(sample: dict[str, Any], cond: str, client: AIClient, judge: QualityValidator, conn: sqlite3.Connection, pool: ProcessPoolExecutor |
            None, pytest_timeout: int, venv_manifest: dict[str, dict[str, str]] | None = None, db_lock: 'threading.Lock | None' = None) -> None:
    sample_id = sample['sample_id']
    t0 = time.perf_counter()
    try:
        row = run_one(
            sample,
            cond,
            client,
            judge,
            pytest_pool=pool,
            pytest_timeout=pytest_timeout,
            venv_manifest=venv_manifest)
    except Exception:
        log.exception('run_one failed for %s/%s', sample_id, cond)
        return
    try:
        _persist_row(conn, row, db_lock)
    except sqlite3.IntegrityError as exc:
        log.warning('DB insert skipped for %s/%s: %s', sample_id, cond, exc)
        return
    elapsed = time.perf_counter() - t0
    log.info(
        '[%s/%s] applied=%s accepted=%s tests=%d/%d (%s) %.1fs',
        sample_id,
        cond,
        row['patch_applied'],
        row['patch_accepted'],
        row['tests_passed'],
        row['tests_targeted'],
        row['tests_selection_method'],
        elapsed)


def main() -> None:
    parser = argparse.ArgumentParser(description='Faza 4C single-pass orchestrator')
    parser.add_argument('--samples', nargs='*', help='restrict to given sample_ids')
    parser.add_argument(
        '--conditions',
        nargs='*',
        default=list(ALL_CONDITIONS),
        choices=list(ALL_CONDITIONS))
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='re-run even if (sample, condition) already in v2')
    parser.add_argument('--pytest-workers', type=int, default=4)
    parser.add_argument('--pytest-timeout', type=int, default=180)
    parser.add_argument(
        '--serial-llm',
        action='store_true',
        help='disable inter-condition threading')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()
    _setup_logging(args.verbose)
    run(sample_ids=args.samples,
        conditions=args.conditions,
        limit=args.limit,
        skip_existing=not args.no_skip,
        pytest_workers=args.pytest_workers,
        pytest_timeout=args.pytest_timeout,
        serial_llm=args.serial_llm)


if __name__ == '__main__':
    main()
