from __future__ import annotations
import json
import sqlite3
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.validator import TestResult, measure_metrics, validate_refactoring
from src.prompts import build_prompt
from src.patch_generator import generate_patch, strip_markdown_fences, validate_patch
from src.config import BUDGET, DATA_DIR, DB_PATH, MODELS
from src.audit_logger import AuditLogger
from src.ai_client import AIClient
sys.stdout.reconfigure(encoding='utf-8')


def load_samples() -> dict[str, dict]:
    path = DATA_DIR / 'samples' / 'functions_sample.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    return {s['sample_id']: s for s in data}


def read_snapshot(sample_id: str) -> str:
    snapshot_path = DATA_DIR / 'snapshots' / f'{sample_id}.py'
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


def get_too_large_samples(condition: str) -> list[str]:
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        "SELECT sample_id FROM experiment_results WHERE condition = ? AND rejection_reason = 'too_large'",
        (condition,
         )).fetchall()
    conn.close()
    return [r[0] for r in rows]


def update_db_row(sample_id: str, condition: str, *, cc_after: float | None, mi_after: float | None, loc_after: int | None, patch_accepted: int, rejection_reason: str | None,
                  changed_pct: float | None, tokens_in: int = 0, tokens_out: int = 0, cost_usd: float = 0.0, response_time_s: float = 0.0, refused: int = 0, audit_log_path: str = '') -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        'UPDATE experiment_results\n           SET cc_after = ?,\n               mi_after = ?,\n               loc_after = ?,\n               patch_accepted = ?,\n               rejection_reason = ?,\n               changed_pct = ?,\n               tokens_in = ?,\n               tokens_out = ?,\n               cost_usd = ?,\n               response_time_s = ?,\n               refused = ?,\n               audit_log_path = ?\n           WHERE sample_id = ? AND condition = ?',
        (cc_after,
         mi_after,
         loc_after,
         patch_accepted,
         rejection_reason,
         changed_pct,
         tokens_in,
         tokens_out,
         cost_usd,
         response_time_s,
         refused,
         audit_log_path,
         sample_id,
         condition))
    conn.commit()
    conn.close()


def revalidate_condition(condition: str, samples: dict[str, dict]) -> None:
    too_large_ids = get_too_large_samples(condition)
    if not too_large_ids:
        print(f'  No too_large samples for condition {condition}. Skipping.')
        return
    provider = MODELS[condition]['provider']
    budget_limit = BUDGET.get(provider, 50.0)
    model_cfg = MODELS[condition]
    print(f"  Model: {model_cfg['name']} | Provider: {provider}")
    print(f'  Budget: ${budget_limit:.2f}')
    print(f'  Samples to revalidate: {len(too_large_ids)}')
    print()
    client = AIClient()
    logger = AuditLogger()
    accepted = 0
    rejected = 0
    errors = 0
    t0 = time.time()
    for i, sid in enumerate(too_large_ids, 1):
        sample = samples.get(sid)
        if not sample:
            print(f'  [{i:3d}/{len(too_large_ids)}] ! {sid:20s} — sample not found', flush=True)
            errors += 1
            continue
        if client.total_cost > budget_limit * 0.95:
            print(f'\n  !! BUDGET ALERT: ${client.total_cost:.4f} / ${budget_limit:.2f} — stopping')
            break
        try:
            original_code = read_snapshot(sid)
            metrics_before = measure_metrics(original_code)
            messages = build_prompt(sample, original_code)
            ai_resp = client.complete(messages, model_cfg)
            refactored_code = strip_markdown_fences(ai_resp.content)
            if refactored_code.strip() == original_code.strip():
                update_db_row(
                    sid,
                    condition,
                    cc_after=metrics_before['cc'],
                    mi_after=metrics_before['mi'],
                    loc_after=metrics_before['loc'],
                    patch_accepted=0,
                    rejection_reason='model_refused',
                    changed_pct=0.0,
                    tokens_in=ai_resp.tokens_in,
                    tokens_out=ai_resp.tokens_out,
                    cost_usd=ai_resp.cost_usd,
                    response_time_s=ai_resp.response_time_s,
                    refused=1)
                status = '-'
                reason = 'model_refused'
                rejected += 1
            else:
                patch = generate_patch(original_code, refactored_code, sample.get('file_path', ''))
                pv = validate_patch(patch, refactored_code)
                if not pv.is_valid:
                    update_db_row(
                        sid,
                        condition,
                        cc_after=metrics_before['cc'],
                        mi_after=metrics_before['mi'],
                        loc_after=metrics_before['loc'],
                        patch_accepted=0,
                        rejection_reason=pv.rejection_reason,
                        changed_pct=pv.changed_pct,
                        tokens_in=ai_resp.tokens_in,
                        tokens_out=ai_resp.tokens_out,
                        cost_usd=ai_resp.cost_usd,
                        response_time_s=ai_resp.response_time_s)
                    status = '-'
                    reason = pv.rejection_reason or 'unknown'
                    rejected += 1
                else:
                    metrics_after = measure_metrics(refactored_code)
                    vd = validate_refactoring(
                        metrics_before, metrics_after, TestResult(
                            passed=0, total=0, duration_s=0.0))
                    audit_data = {
                        'sample_id': sid,
                        'condition': condition,
                        'model': ai_resp.model,
                        'decision': 'ACCEPT' if vd.accepted else 'REJECT',
                        'error': None if vd.accepted else vd.reason,
                        'tokens_in': ai_resp.tokens_in,
                        'tokens_out': ai_resp.tokens_out,
                        'cost_usd': ai_resp.cost_usd,
                        'response_time_s': ai_resp.response_time_s,
                        'refused': False,
                        'metrics_before': metrics_before,
                        'metrics_after': metrics_after,
                        'patch_length': len(patch),
                        'changed_pct': pv.changed_pct,
                        'revalidation': True}
                    audit_path = logger.log_step(audit_data)
                    update_db_row(
                        sid,
                        condition,
                        cc_after=metrics_after['cc'],
                        mi_after=metrics_after['mi'],
                        loc_after=metrics_after['loc'],
                        patch_accepted=1 if vd.accepted else 0,
                        rejection_reason=None if vd.accepted else vd.reason,
                        changed_pct=pv.changed_pct,
                        tokens_in=ai_resp.tokens_in,
                        tokens_out=ai_resp.tokens_out,
                        cost_usd=ai_resp.cost_usd,
                        response_time_s=ai_resp.response_time_s,
                        audit_log_path=audit_path)
                    if vd.accepted:
                        status = '+'
                        reason = 'ok'
                        accepted += 1
                    else:
                        status = '-'
                        reason = vd.reason or 'no_improvement'
                        rejected += 1
            elapsed = time.time() - t0
            eta = elapsed / i * (len(too_large_ids) - i)
            print(
                f'  [{i:3d}/{len(too_large_ids)}] {status} {sid:20s} ${ai_resp.cost_usd:.4f}  ETA {eta / 60:.0f}m  ({reason})',
                flush=True)
        except Exception as exc:
            errors += 1
            print(f'  [{i:3d}/{len(too_large_ids)}] ! {sid:20s} ERROR: {exc}', flush=True)
    total_time = time.time() - t0
    print(f'\n  Condition {condition} revalidation complete:')
    print(f'    Accepted:  {accepted}')
    print(f'    Rejected:  {rejected}')
    print(f'    Errors:    {errors}')
    print(f'    Cost:      ${client.total_cost:.4f}')
    print(f'    Duration:  {total_time:.1f}s ({total_time / 60:.1f}m)')


def main() -> None:
    conditions = sys.argv[1:] if len(sys.argv) > 1 else ['A', 'G', 'C']
    for c in conditions:
        if c not in MODELS:
            print(f'Unknown condition: {c}')
            sys.exit(1)
    samples = load_samples()
    print(f'Loaded {len(samples)} samples')
    print(f"{'=' * 60}")
    for condition in conditions:
        print(f"\n{'=' * 60}")
        print(f'REVALIDATING CONDITION {condition}')
        print(f"{'=' * 60}")
        revalidate_condition(condition, samples)
    print(f"\n{'=' * 60}")
    print('REVALIDATION COMPLETE — verifying results...')
    print(f"{'=' * 60}")
    conn = sqlite3.connect(str(DB_PATH))
    for c in conditions:
        total = conn.execute(
            'SELECT COUNT(*) FROM experiment_results WHERE condition=?', (c,)).fetchone()[0]
        tl = conn.execute(
            "SELECT COUNT(*) FROM experiment_results WHERE condition=? AND rejection_reason='too_large'",
            (c,
             )).fetchone()[0]
        acc = conn.execute(
            'SELECT COUNT(*) FROM experiment_results WHERE condition=? AND patch_accepted=1',
            (c,
             )).fetchone()[0]
        nmi = conn.execute(
            "SELECT COUNT(*) FROM experiment_results WHERE condition=? AND rejection_reason='no_metric_improvement'",
            (c,
             )).fetchone()[0]
        mr = conn.execute(
            "SELECT COUNT(*) FROM experiment_results WHERE condition=? AND (rejection_reason='model_refused' OR refused=1)",
            (c,
             )).fetchone()[0]
        print(f'  {c}: {total} total, {acc} accepted, {tl} too_large, {nmi} no_improve, {mr} refused')
    conn.close()


if __name__ == '__main__':
    main()
