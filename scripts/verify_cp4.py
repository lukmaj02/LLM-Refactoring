import sqlite3
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
print('=' * 60)
print('CP-4 VERIFICATION')
print('=' * 60)
print('\n1. Records per condition:')
rows = conn.execute('\n    SELECT condition, COUNT(*), SUM(patch_accepted),\n           ROUND(AVG(CASE WHEN patch_accepted=1 THEN cc_before-cc_after END), 2) as avg_cc_delta,\n           ROUND(SUM(cost_usd), 4) as total_cost\n    FROM experiment_results GROUP BY condition ORDER BY condition\n').fetchall()
for r in rows:
    print(f'  {r[0]}: {r[1]} rows, {r[2]} accepted, avg CC reduction: {r[3]}, cost: ${r[4]}')
nulls = conn.execute(
    "SELECT COUNT(*) FROM experiment_results WHERE cc_after IS NULL AND condition != 'K'").fetchone()[0]
print(f'\n2. NULL cc_after (non-K): {nulls}')
cost = conn.execute(
    "SELECT ROUND(SUM(cost_usd), 4) FROM experiment_results WHERE condition IN ('A','G','C')").fetchone()[0]
print(f'\n3. Total API cost: ${cost}')
print('\n4. Acceptance by repo x condition:')
rows = conn.execute("\n    SELECT repo, condition, COUNT(*) as n,\n           SUM(patch_accepted) as accepted,\n           ROUND(100.0*SUM(patch_accepted)/COUNT(*), 1) as pct\n    FROM experiment_results\n    WHERE condition != 'K'\n    GROUP BY repo, condition ORDER BY repo, condition\n").fetchall()
for r in rows:
    print(f'  {r[0]:12s} {r[1]}: {r[3]:2d}/{r[2]:2d} ({r[4]:5.1f}%)')
print('\n5. Rejection reasons (non-K):')
rows = conn.execute("\n    SELECT rejection_reason, COUNT(*) FROM experiment_results\n    WHERE condition != 'K' AND patch_accepted = 0 AND rejection_reason IS NOT NULL\n    GROUP BY rejection_reason ORDER BY COUNT(*) DESC\n").fetchall()
for r in rows:
    print(f'  {r[0]:25s}: {r[1]}')
logs = list(Path('logs').glob('audit_*.json'))
print(f'\n6. Audit log files: {len(logs)}')
conn.close()
print('\n' + '=' * 60)
print('CP-4 VERIFICATION COMPLETE')
