from __future__ import annotations
import argparse
import random
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.quality_validator import QualityValidator
from src.config import DB_PATH
SEED = 42
N_SAMPLES = 50
CONDITIONS = ('A', 'G', 'C')
SCHEMA = '\nCREATE TABLE IF NOT EXISTS {table} (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    sample_id TEXT NOT NULL,\n    condition TEXT NOT NULL,\n    solid_score INTEGER,\n    dry_score INTEGER,\n    kiss_score INTEGER,\n    semantic_score INTEGER,\n    quality_score INTEGER,\n    rationale TEXT,\n    cost_usd REAL,\n    judged_code_path TEXT,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,\n    UNIQUE(sample_id, condition)\n);\n'


def pick_pairs(con: sqlite3.Connection) -> list[tuple[str, str, str]]:
    rows = con.execute("SELECT sample_id, condition, refactored_code_path\n           FROM experiment_results_v2\n           WHERE phase='4C' AND refactored_code_path IS NOT NULL\n             AND quality_score IS NOT NULL AND condition IN ('A','G','C')").fetchall()
    by_sample: dict[str, dict[str, str]] = {}
    for sid, cond, path in rows:
        by_sample.setdefault(sid, {})[cond] = path
    common = sorted((s for s, d in by_sample.items() if set(CONDITIONS) <= set(d)))
    rng = random.Random(SEED)
    chosen = rng.sample(common, min(N_SAMPLES, len(common)))
    return [(sid, c, by_sample[sid][c]) for sid in sorted(chosen) for c in CONDITIONS]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--judge', choices=('A', 'G', 'C'), default='G')
    args = ap.parse_args()
    table = 'judge_retest' if args.judge == 'G' else f'judge_retest_{args.judge}'
    con = sqlite3.connect(str(DB_PATH))
    con.execute(SCHEMA.format(table=table))
    con.commit()
    done = {(r[0], r[1]) for r in con.execute(f'SELECT sample_id, condition FROM {table}')}
    pairs = [(s, c, p) for s, c, p in pick_pairs(con) if (s, c) not in done]
    if args.limit:
        pairs = pairs[:args.limit]
    print(f'pary do oceny: {len(pairs)} (pominieto gotowe: {len(done)})')
    if args.dry_run:
        for s, c, p in pairs[:10]:
            print(' ', s, c, p)
        return
    judge = QualityValidator(args.judge)
    snap_dir = ROOT / 'data' / 'snapshots'
    for i, (sid, cond, path) in enumerate(pairs, 1):
        original = (snap_dir / f'{sid}.py').read_text(encoding='utf-8')
        art = Path(path)
        if not art.is_absolute():
            art = ROOT / path
        refactored = art.read_text(encoding='utf-8')
        score = judge.evaluate(original, refactored)
        con.execute(
            f'INSERT OR IGNORE INTO {table}\n               (sample_id, condition, solid_score, dry_score, kiss_score,\n                semantic_score, quality_score, rationale, cost_usd,\n                judged_code_path)\n               VALUES (?,?,?,?,?,?,?,?,?,?)',
            (sid,
             cond,
             score.solid_score,
             score.dry_score,
             score.kiss_score,
             score.semantic_score,
             score.overall_score,
             score.rationale,
             score.cost_usd,
             str(art)))
        con.commit()
        print(f'[{i}/{len(pairs)}] {sid} x {cond}: quality={score.overall_score} semantic={score.semantic_score} (koszt lacznie ${judge.total_cost:.3f})')
    print(f'KONIEC. Koszt sesji: ${judge.total_cost:.3f}')


if __name__ == '__main__':
    main()
