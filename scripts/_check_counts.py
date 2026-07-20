import json
import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
for c in ['A', 'G', 'C', 'T', 'K']:
    total = conn.execute(
        'SELECT COUNT(*) FROM experiment_results WHERE condition=?', (c,)).fetchone()[0]
    unique = conn.execute(
        'SELECT COUNT(DISTINCT sample_id) FROM experiment_results WHERE condition=?', (c,)).fetchone()[0]
    too_large = conn.execute(
        "SELECT COUNT(*) FROM experiment_results WHERE condition=? AND rejection_reason='too_large'",
        (c,
         )).fetchone()[0]
    accepted = conn.execute(
        'SELECT COUNT(*) FROM experiment_results WHERE condition=? AND patch_accepted=1', (c,)).fetchone()[0]
    print(f'{c}: {total} rows, {unique} unique, {too_large} too_large, {accepted} accepted')
conn.close()
