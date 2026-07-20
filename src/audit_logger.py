from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from src.config import LOGS_DIR, RESULTS_DIR


class AuditLogger:

    def __init__(self, log_dir: Path | None = None) -> None:
        self._log_dir = log_dir or LOGS_DIR
        self._log_dir.mkdir(parents=True, exist_ok=True)

    def log_step(self, step_data: dict) -> str:
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')
        sample_id = step_data.get('sample_id', 'unknown')
        condition = step_data.get('condition', 'X')
        filename = f'audit_{sample_id}_{condition}_{ts}.json'
        path = self._log_dir / filename
        record = {'timestamp': datetime.now(timezone.utc).isoformat(), **step_data}
        path.write_text(
            json.dumps(
                record,
                indent=2,
                ensure_ascii=False,
                default=str),
            encoding='utf-8')
        return str(path)

    def log_experiment_summary(self, results: list[dict]) -> str:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        path = RESULTS_DIR / 'experiment_summary.json'
        summary = {
            'generated_at': datetime.now(
                timezone.utc).isoformat(),
            'total_samples': len(results),
            'results': results}
        path.write_text(
            json.dumps(
                summary,
                indent=2,
                ensure_ascii=False,
                default=str),
            encoding='utf-8')
        return str(path)
