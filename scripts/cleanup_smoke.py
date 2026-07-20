import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
deleted = conn.execute("DELETE FROM experiment_results WHERE condition != 'K'").rowcount
conn.commit()
rows = conn.execute(
    'SELECT condition, COUNT(*) FROM experiment_results GROUP BY condition').fetchall()
print(f'Deleted {deleted} smoke rows. Remaining: {rows}')
conn.close()
