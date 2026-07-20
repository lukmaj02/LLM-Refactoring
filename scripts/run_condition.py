from __future__ import annotations
import json
import sqlite3
import sys
import time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH, BUDGET, MODELS, DATA_DIR
from src.arp_pipeline import ARPPipeline
sys.stdout.reconfigure(encoding='utf-8')


def load_samples() -> list[dict]:
    path = DATA_DIR / 'samples' / 'functions_sample.json'
    return json.loads(path.read_text(encoding='utf-8'))


def already_done(condition: str) -> set[str]:
    conn = sqlite3.connect(str(DB_PATH))
    rows = conn.execute(
        'SELECT sample_id FROM experiment_results WHERE condition = ?',
        (condition,
         )).fetchall()
    conn.close()
    return {r[0] for r in rows}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ('T', 'A', 'G', 'C'):
        print('Usage: python scripts/run_condition.py [T|A|G|C]')
        sys.exit(1)
    condition = sys.argv[1]
    samples = load_samples()
    done = already_done(condition)
    todo = [s for s in samples if s['sample_id'] not in done]
    provider = MODELS.get(condition, {}).get('provider', 'local')
    budget_limit = BUDGET.get(provider, 50.0)
    print(f"{'=' * 60}")
    print(f"CONDITION {condition} | Model: {MODELS.get(condition, {}).get('name', 'traditional')}")
    print(f'Samples: {len(samples)} total, {len(done)} done, {len(todo)} remaining')
    print(f'Budget: ${budget_limit:.2f} ({provider})')
    print(f"{'=' * 60}")
    if not todo:
        print('All samples already processed. Nothing to do.')
        return
    pipeline = ARPPipeline()
    accepted = 0
    rejected = 0
    errors = 0
    t0 = time.time()
    for i, sample in enumerate(todo, 1):
        sid = sample['sample_id']
        if condition != 'T' and pipeline.total_cost > budget_limit * 0.95:
            print(f'\n!! BUDGET ALERT: ${pipeline.total_cost:.4f} / ${budget_limit:.2f} — stopping')
            break
        result = pipeline.run(sample, condition)
        status_char = {
            'ACCEPT': '+',
            'REJECT': '-',
            'ERROR': '!',
            'SKIPPED': '~'}.get(
            result.decision,
            '?')
        cost_str = f'${result.ai_response.cost_usd:.4f}' if result.ai_response else '$0'
        if result.decision == 'ACCEPT':
            accepted += 1
        elif result.decision == 'REJECT':
            rejected += 1
        else:
            errors += 1
        elapsed = time.time() - t0
        eta = elapsed / i * (len(todo) - i)
        print(f"  [{i:3d}/{len(todo)}] {status_char} {sid:20s} CC {result.metrics_before.get('cc', '?')}->{result.metrics_after.get('cc', '?')} MI {result.metrics_before.get('mi', '?')}->{result.metrics_after.get('mi', '?')} {cost_str:>8s}  ETA {eta / 60:.0f}m  ({result.error or 'ok'})", flush=True)
    total_time = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f'CONDITION {condition} COMPLETE')
    print(f'  Accepted:  {accepted}')
    print(f'  Rejected:  {rejected}')
    print(f'  Errors:    {errors}')
    print(f'  Total cost: ${pipeline.total_cost:.4f}')
    print(f'  Duration:  {total_time:.1f}s ({total_time / 60:.1f}m)')
    print(f"{'=' * 60}")
    export_condition_json(condition)


def export_condition_json(condition: str) -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    rows = conn.execute('SELECT * FROM experiment_results WHERE condition = ?',
                        (condition,)).fetchall()
    conn.close()
    data = [dict(r) for r in rows]
    out = DATA_DIR / 'results' / f'condition_{condition}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
    print(f'Exported {len(data)} rows to {out}')


if __name__ == '__main__':
    main()
