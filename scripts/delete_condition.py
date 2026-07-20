import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
cond = sys.argv[1]
conn = sqlite3.connect(str(DB_PATH))
d = conn.execute('DELETE FROM experiment_results WHERE condition=?', (cond,)).rowcount
conn.commit()
print(f'Deleted {d} rows for condition {cond}')
conn.close()
