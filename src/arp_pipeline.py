from __future__ import annotations
import logging
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from src.ai_client import AIClient, AIResponse
from src.audit_logger import AuditLogger
from src.config import DATA_DIR, DB_PATH, MODELS, ROOT
from src.patch_generator import generate_patch, strip_markdown_fences, validate_patch
from src.prompts import build_prompt
from src.validator import TestResult, ValidationDecision, measure_metrics, validate_refactoring
log = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    sample_id: str
    condition: str
    decision: str = 'PENDING'
    metrics_before: dict = field(default_factory=dict)
    metrics_after: dict = field(default_factory=dict)
    ai_response: AIResponse | None = None
    validation: ValidationDecision | None = None
    patch: str = ''
    changed_pct: float = 0.0
    audit_path: str = ''
    error: str | None = None


class ARPPipeline:

    def __init__(self) -> None:
        self._client = AIClient()
        self._logger = AuditLogger()

    @property
    def total_cost(self) -> float:
        return self._client.total_cost

    def run(self, sample: dict, condition: str) -> PipelineResult:
        sample_id = sample['sample_id']
        result = PipelineResult(sample_id=sample_id, condition=condition)
        try:
            snapshot_path = DATA_DIR / 'snapshots' / f'{sample_id}.py'
            if not snapshot_path.exists():
                result.decision = 'ERROR'
                result.error = f'Snapshot not found: {snapshot_path}'
                return result
            original_code = self._read_code(snapshot_path)
            result.metrics_before = measure_metrics(original_code)
            if condition == 'K':
                result.decision = 'SKIPPED'
                result.metrics_after = result.metrics_before.copy()
                return result
            if condition == 'T':
                refactored_code = self._apply_traditional(original_code)
                ai_resp = None
            else:
                ai_resp = self._call_ai(sample, original_code, condition)
                result.ai_response = ai_resp
                refactored_code = strip_markdown_fences(ai_resp.content)
                if refactored_code.strip() == original_code.strip():
                    ai_resp.refused = True
                    result.decision = 'REJECT'
                    result.error = 'model_refused'
                    result.metrics_after = result.metrics_before.copy()
                    self._log_and_persist(result, sample)
                    return result
            patch = generate_patch(original_code, refactored_code, sample.get('file_path', ''))
            pv = validate_patch(patch, refactored_code)
            result.patch = patch
            result.changed_pct = pv.changed_pct
            if not pv.is_valid:
                result.decision = 'REJECT'
                result.error = pv.rejection_reason
                result.metrics_after = result.metrics_before.copy()
                self._log_and_persist(result, sample)
                return result
            result.metrics_after = measure_metrics(refactored_code)
            vd = validate_refactoring(
                result.metrics_before, result.metrics_after, TestResult(
                    passed=0, total=0, duration_s=0.0))
            result.validation = vd
            result.decision = 'ACCEPT' if vd.accepted else 'REJECT'
            if not vd.accepted:
                result.error = vd.reason
        except Exception as exc:
            log.exception('Pipeline error for %s/%s', sample_id, condition)
            result.decision = 'ERROR'
            result.error = str(exc)
        self._log_and_persist(result, sample)
        return result

    @staticmethod
    def _read_code(snapshot_path: Path) -> str:
        lines = snapshot_path.read_text(encoding='utf-8').splitlines(keepends=True)
        code_lines: list[str] = []
        header_done = False
        for line in lines:
            if not header_done and line.startswith('# '):
                continue
            header_done = True
            code_lines.append(line)
        while code_lines and (not code_lines[0].strip()):
            code_lines.pop(0)
        return ''.join(code_lines)

    def _call_ai(self, sample: dict, code: str, condition: str) -> AIResponse:
        model_cfg = MODELS[condition]
        messages = build_prompt(sample, code)
        return self._client.complete(messages, model_cfg)

    @staticmethod
    def _apply_traditional(code: str) -> str:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp = Path(f.name)
        try:
            subprocess.run([sys.executable,
                            '-m',
                            'autopep8',
                            '--in-place',
                            '--aggressive',
                            '--aggressive',
                            str(tmp)],
                           capture_output=True,
                           timeout=30)
            subprocess.run([sys.executable,
                            '-m',
                            'autoflake',
                            '--in-place',
                            '--remove-all-unused-imports',
                            str(tmp)],
                           capture_output=True,
                           timeout=30)
            return tmp.read_text(encoding='utf-8')
        finally:
            tmp.unlink(missing_ok=True)

    def _log_and_persist(self, result: PipelineResult, sample: dict) -> None:
        ai = result.ai_response
        audit_data = {
            'sample_id': result.sample_id,
            'condition': result.condition,
            'model': ai.model if ai else None,
            'decision': result.decision,
            'error': result.error,
            'tokens_in': ai.tokens_in if ai else 0,
            'tokens_out': ai.tokens_out if ai else 0,
            'cost_usd': ai.cost_usd if ai else 0.0,
            'response_time_s': ai.response_time_s if ai else 0.0,
            'refused': ai.refused if ai else False,
            'metrics_before': result.metrics_before,
            'metrics_after': result.metrics_after,
            'patch_length': len(
                result.patch)}
        result.audit_path = self._logger.log_step(audit_data)
        self._insert_db(result, sample)

    def _insert_db(self, result: PipelineResult, sample: dict) -> None:
        ai = result.ai_response
        mb = result.metrics_before
        ma = result.metrics_after
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH))
        try:
            conn.execute('INSERT INTO experiment_results (\n                    sample_id, repo, file_path, function_name, condition,\n                    cc_before, mi_before, loc_before,\n                    cc_after, mi_after, loc_after,\n                    patch_applied, patch_accepted,\n                    rejection_reason, model_name,\n                    tokens_in, tokens_out, cost_usd, response_time_s,\n                    refused, audit_log_path, changed_pct\n                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                         (result.sample_id, sample.get('repo', ''), sample.get('file_path', ''), sample.get('function_name', ''), result.condition, mb.get('cc'), mb.get('mi'), mb.get('loc'), ma.get('cc'), ma.get('mi'), ma.get('loc'), 1 if result.decision in ('ACCEPT', 'REJECT') else 0, 1 if result.decision == 'ACCEPT' else 0, result.error, ai.model if ai else None, ai.tokens_in if ai else 0, ai.tokens_out if ai else 0, ai.cost_usd if ai else 0.0, ai.response_time_s if ai else 0.0, 1 if ai and ai.refused else 0, result.audit_path, result.changed_pct))
            conn.commit()
        finally:
            conn.close()
