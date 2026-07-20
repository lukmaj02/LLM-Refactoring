import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
print('=== ACCEPTANCE RATES ===')
for c in ['K', 'T', 'A', 'G', 'C']:
    total = conn.execute(
        'SELECT COUNT(*) FROM experiment_results WHERE condition=?', (c,)).fetchone()[0]
    acc = conn.execute(
        'SELECT COUNT(*) FROM experiment_results WHERE condition=? AND patch_accepted=1',
        (c,
         )).fetchone()[0]
    print(f'  {c}: {acc}/{total} ({100 * acc / total:.1f}%)')
print('\n=== REJECTION REASONS (AI conditions) ===')
for c in ['A', 'G', 'C']:
    print(f'  {c}:')
    rows = conn.execute(
        'SELECT rejection_reason, COUNT(*) as cnt FROM experiment_results WHERE condition=? GROUP BY rejection_reason ORDER BY cnt DESC',
        (c,
         )).fetchall()
    for reason, cnt in rows:
        label = reason if reason else 'accepted'
        print(f'    {label}: {cnt}')
print('\n=== QUALITY SCORES ===')
for c in ['A', 'G', 'C']:
    row = conn.execute(
        'SELECT COUNT(*), AVG(quality_score), AVG(solid_score), AVG(dry_score),\n           AVG(kiss_score), AVG(semantic_score)\n           FROM experiment_results WHERE condition=? AND quality_score IS NOT NULL',
        (c,
         )).fetchone()
    n, q, s, d, k, sem = row
    print(f'  {c}: n={n}, Quality={q:.1f}, SOLID={s:.1f}, DRY={d:.1f}, KISS={k:.1f}, Semantic={sem:.1f}')
print('\n=== CC CHANGES (accepted only) ===')
for c in ['T', 'A', 'G', 'C']:
    row = conn.execute(
        'SELECT AVG(cc_before), AVG(cc_after), AVG(cc_before - cc_after), COUNT(*)\n           FROM experiment_results WHERE condition=? AND patch_accepted=1',
        (c,
         )).fetchone()
    if row[0]:
        print(
            f'  {c}: CC_before={row[0]:.1f}, CC_after={row[1]:.1f}, delta={row[2]:.1f}, n={row[3]}')
print('\n=== MI CHANGES (accepted only) ===')
for c in ['T', 'A', 'G', 'C']:
    row = conn.execute(
        'SELECT AVG(mi_before), AVG(mi_after), AVG(mi_after - mi_before), COUNT(*)\n           FROM experiment_results WHERE condition=? AND patch_accepted=1',
        (c,
         )).fetchone()
    if row[0]:
        print(
            f'  {c}: MI_before={row[0]:.1f}, MI_after={row[1]:.1f}, delta={row[2]:.1f}, n={row[3]}')
print('\n=== COSTS (from original experiment) ===')
for c in ['A', 'G', 'C']:
    row = conn.execute(
        'SELECT SUM(cost_usd) FROM experiment_results WHERE condition=?', (c,)).fetchone()
    val = row[0] or 0
    print(f'  {c}: ${val:.4f}')
print('\n=== CHANGED_PCT (accepted AI samples) ===')
for c in ['A', 'G', 'C']:
    row = conn.execute(
        'SELECT AVG(changed_pct), MIN(changed_pct), MAX(changed_pct), COUNT(*)\n           FROM experiment_results WHERE condition=? AND patch_accepted=1 AND changed_pct IS NOT NULL',
        (c,
         )).fetchone()
    if row[0] is not None:
        print(f'  {c}: avg={row[0]:.2f}, min={row[1]:.2f}, max={row[2]:.2f}, n={row[3]}')
conn.close()
