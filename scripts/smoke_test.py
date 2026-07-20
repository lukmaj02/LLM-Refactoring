from __future__ import annotations
import json
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
from src.arp_pipeline import ARPPipeline
sys.stdout.reconfigure(encoding='utf-8')
SAMPLE = {
    'sample_id': 'requests_001',
    'repo': 'requests',
    'file_path': 'data/repos/requests/requests/models.py',
    'function_name': 'prepare_body',
    'cc': 5,
    'mi': 73.0}


def main() -> None:
    pipeline = ARPPipeline()
    errors: list[str] = []
    print('=' * 60)
    print('TEST 1: Condition K (control — no changes)')
    r_k = pipeline.run(SAMPLE, condition='K')
    print(f'  Decision: {r_k.decision}')
    print(f'  Metrics:  {r_k.metrics_before}')
    if r_k.decision != 'SKIPPED':
        errors.append(f'K: expected SKIPPED, got {r_k.decision}')
    print('  -> PASS' if not errors else f'  -> FAIL: {errors[-1]}')
    print('=' * 60)
    print('TEST 2: Condition T (autopep8 + autoflake)')
    r_t = pipeline.run(SAMPLE, condition='T')
    print(f'  Decision: {r_t.decision}')
    print(f"  Before: CC={r_t.metrics_before.get('cc')}, MI={r_t.metrics_before.get('mi')}")
    print(f"  After:  CC={r_t.metrics_after.get('cc')}, MI={r_t.metrics_after.get('mi')}")
    if r_t.decision not in ('ACCEPT', 'REJECT'):
        errors.append(f'T: unexpected decision {r_t.decision}')
    print(f'  -> PASS (decision={r_t.decision})')
    print('=' * 60)
    print('TEST 3: Condition G (Gemini 2.5 Flash — free)')
    r_g = pipeline.run(SAMPLE, condition='G')
    print(f'  Decision: {r_g.decision}')
    if r_g.ai_response:
        print(f'  Tokens:   {r_g.ai_response.tokens_in} in / {r_g.ai_response.tokens_out} out')
        print(f'  Cost:     ${r_g.ai_response.cost_usd:.6f}')
        print(f'  Time:     {r_g.ai_response.response_time_s}s')
    print(f"  Before: CC={r_g.metrics_before.get('cc')}, MI={r_g.metrics_before.get('mi')}")
    print(f"  After:  CC={r_g.metrics_after.get('cc')}, MI={r_g.metrics_after.get('mi')}")
    if r_g.audit_path:
        print(f'  Audit:  {r_g.audit_path}')
    if r_g.decision == 'ERROR':
        errors.append(f'G: error — {r_g.error}')
    print(f'  -> PASS (decision={r_g.decision})')
    print('=' * 60)
    print('VERIFYING DATABASE')
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT condition, patch_accepted, cc_before, cc_after, cost_usd FROM experiment_results WHERE sample_id='requests_001' AND condition != 'K' ORDER BY timestamp DESC").fetchall()
    conn.close()
    print(f'  Smoke-test rows in DB: {len(rows)}')
    for r in rows:
        print(f'    {r}')
    if len(rows) < 2:
        errors.append(f'DB: expected >= 2 non-K rows, got {len(rows)}')
    print('=' * 60)
    if errors:
        print(f'SMOKE TEST FAILED ({len(errors)} errors):')
        for e in errors:
            print(f'  - {e}')
        sys.exit(1)
    else:
        print('SMOKE TEST PASSED')
        print(f'  Total API cost: ${pipeline.total_cost:.6f}')
        sys.exit(0)


if __name__ == '__main__':
    main()
