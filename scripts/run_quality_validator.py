from __future__ import annotations
import json
import sqlite3
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.quality_validator import QualityValidator
from src.prompts import build_prompt
from src.patch_generator import strip_markdown_fences
from src.config import BUDGET, DATA_DIR, DB_PATH, MODELS
from src.ai_client import AIClient
sys.stdout.reconfigure(encoding='utf-8')


def load_samples() -> dict[str, dict]:
    path = DATA_DIR / 'samples' / 'functions_sample.json'
    return {s['sample_id']: s for s in json.loads(path.read_text(encoding='utf-8'))}


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


def get_samples_needing_quality(condition: str) -> list[dict]:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT sample_id, rejection_reason, refused, quality_score\n           FROM experiment_results\n           WHERE condition = ?\n             AND quality_score IS NULL\n             AND (rejection_reason IS NULL\n                  OR rejection_reason = 'no_metric_improvement')\n             AND refused = 0", (condition,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_quality(sample_id: str, condition: str, scores: dict) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        'UPDATE experiment_results\n           SET solid_score = ?,\n               dry_score = ?,\n               kiss_score = ?,\n               semantic_score = ?,\n               quality_score = ?,\n               quality_rationale = ?\n           WHERE sample_id = ? AND condition = ?',
        (scores['solid_score'],
         scores['dry_score'],
         scores['kiss_score'],
         scores['semantic_score'],
         scores['overall_score'],
         scores['rationale'],
         sample_id,
         condition))
    conn.commit()
    conn.close()


def run_quality_for_condition(condition: str, all_samples: dict[str, dict]) -> None:
    need_quality = get_samples_needing_quality(condition)
    if not need_quality:
        print(f'  No samples needing quality evaluation for {condition}.')
        return
    provider = MODELS[condition]['provider']
    model_cfg = MODELS[condition]
    refactor_budget = BUDGET.get(provider, 50.0)
    print(f"  Model (refactor): {model_cfg['name']} | Provider: {provider}")
    print(f'  Validator: Gemini 2.5 Flash')
    print(f'  Samples to evaluate: {len(need_quality)}')
    print()
    refactor_client = AIClient(max_retries=5, base_delay=3.0)
    validator = QualityValidator(model_condition='G')
    evaluated = 0
    skipped = 0
    errors = 0
    t0 = time.time()
    for i, row in enumerate(need_quality, 1):
        sid = row['sample_id']
        sample = all_samples.get(sid)
        if not sample:
            print(f'  [{i:3d}/{len(need_quality)}] ! {sid:20s} sample not found', flush=True)
            errors += 1
            continue
        if refactor_client.total_cost > refactor_budget * 0.95:
            print(f'\n  !! REFACTOR BUDGET ALERT: ${refactor_client.total_cost:.4f} — stopping')
            break
        try:
            original_code = read_snapshot(sid)
            messages = build_prompt(sample, original_code)
            ai_resp = refactor_client.complete(messages, model_cfg)
            refactored_code = strip_markdown_fences(ai_resp.content)
            if refactored_code.strip() == original_code.strip():
                skipped += 1
                print(
                    f'  [{i:3d}/{len(need_quality)}] ~ {sid:20s} model_refused (skip)',
                    flush=True)
                continue
            qs = validator.evaluate(original_code, refactored_code)
            update_quality(sid,
                           condition,
                           {'solid_score': qs.solid_score,
                            'dry_score': qs.dry_score,
                            'kiss_score': qs.kiss_score,
                            'semantic_score': qs.semantic_score,
                            'overall_score': qs.overall_score,
                            'rationale': qs.rationale})
            elapsed = time.time() - t0
            eta = elapsed / i * (len(need_quality) - i) if i > 0 else 0
            print(f'  [{i:3d}/{len(need_quality)}] + {sid:20s} Q={qs.overall_score} S={qs.solid_score} D={qs.dry_score} K={qs.kiss_score} Sem={qs.semantic_score}  ${ai_resp.cost_usd + qs.cost_usd:.4f}  ETA {eta / 60:.0f}m', flush=True)
            evaluated += 1
        except Exception as exc:
            errors += 1
            print(f'  [{i:3d}/{len(need_quality)}] ! {sid:20s} ERROR: {exc}', flush=True)
    total_time = time.time() - t0
    print(f'\n  Condition {condition} quality evaluation complete:')
    print(f'    Evaluated: {evaluated}')
    print(f'    Skipped:   {skipped}')
    print(f'    Errors:    {errors}')
    print(f'    Refactor cost: ${refactor_client.total_cost:.4f}')
    print(f'    Validator cost: ${validator.total_cost:.4f}')
    print(f'    Duration: {total_time:.1f}s ({total_time / 60:.1f}m)')


def main() -> None:
    conditions = sys.argv[1:] if len(sys.argv) > 1 else ['A', 'G', 'C']
    for c in conditions:
        if c not in MODELS:
            print(f'Unknown condition: {c}')
            sys.exit(1)
    samples = load_samples()
    print(f'Loaded {len(samples)} samples')
    for condition in conditions:
        print(f"\n{'=' * 60}")
        print(f'QUALITY EVALUATION — CONDITION {condition}')
        print(f"{'=' * 60}")
        run_quality_for_condition(condition, samples)
    print(f"\n{'=' * 60}")
    print('QUALITY EVALUATION COMPLETE')
    print(f"{'=' * 60}")
    conn = sqlite3.connect(str(DB_PATH))
    for c in conditions:
        with_score = conn.execute(
            'SELECT COUNT(*) FROM experiment_results WHERE condition=? AND quality_score IS NOT NULL',
            (c,
             )).fetchone()[0]
        avg_q = conn.execute(
            'SELECT AVG(quality_score) FROM experiment_results WHERE condition=? AND quality_score IS NOT NULL',
            (c,
             )).fetchone()[0]
        total = conn.execute(
            'SELECT COUNT(*) FROM experiment_results WHERE condition=?', (c,)).fetchone()[0]
        print(f'  {c}: {with_score}/{total} with quality scores, avg={avg_q:.1f}' if avg_q else f'  {c}: {with_score}/{total} with quality scores')
    conn.close()


if __name__ == '__main__':
    main()
