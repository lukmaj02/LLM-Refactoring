import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
r = conn.execute('SELECT condition, COUNT(*) FROM experiment_results GROUP BY condition').fetchall()
print('Before:', r)
dups = conn.execute(
    "SELECT sample_id, COUNT(*) as c FROM experiment_results WHERE condition='G' GROUP BY sample_id HAVING c > 1").fetchall()
print(f'Duplicate G sample_ids: {len(dups)}')
if dups:
    conn.execute("\n        DELETE FROM experiment_results\n        WHERE condition='G' AND id NOT IN (\n            SELECT MAX(id) FROM experiment_results WHERE condition='G' GROUP BY sample_id\n        )\n    ")
    conn.commit()
r2 = conn.execute(
    'SELECT condition, COUNT(*) FROM experiment_results GROUP BY condition').fetchall()
print('After:', r2)
conn.close()
