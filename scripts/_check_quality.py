import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
for c in ['A', 'G', 'C']:
    total = conn.execute(
        'SELECT COUNT(*) FROM experiment_results WHERE condition=?', (c,)).fetchone()[0]
    with_q = conn.execute(
        'SELECT COUNT(*) FROM experiment_results WHERE condition=? AND quality_score IS NOT NULL',
        (c,
         )).fetchone()[0]
    need = conn.execute(
        "SELECT COUNT(*) FROM experiment_results \n        WHERE condition=? AND quality_score IS NULL \n        AND (rejection_reason IS NULL OR rejection_reason='no_metric_improvement')\n        AND refused=0",
        (c,
         )).fetchone()[0]
    print(f'{c}: {total} total, {with_q} with quality, {need} needing evaluation')
conn.close()
