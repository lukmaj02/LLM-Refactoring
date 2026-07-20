import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import DB_PATH
NEW_COLUMNS = [('changed_pct', 'REAL'), ('solid_score', 'INTEGER'), ('dry_score', 'INTEGER'), ('kiss_score',
                                                                                               'INTEGER'), ('semantic_score', 'INTEGER'), ('quality_score', 'INTEGER'), ('quality_rationale', 'TEXT')]
conn = sqlite3.connect(str(DB_PATH))
existing = {row[1] for row in conn.execute('PRAGMA table_info(experiment_results)')}
added = []
for col, typ in NEW_COLUMNS:
    if col not in existing:
        conn.execute(f'ALTER TABLE experiment_results ADD COLUMN {col} {typ}')
        added.append(col)
conn.commit()
print(f'Added {len(added)} columns: {added}')
cols = [row[1] for row in conn.execute('PRAGMA table_info(experiment_results)')]
print(f'Total columns: {len(cols)}')
conn.close()
