import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
conn = sqlite3.connect(str(DB_PATH))
conn.execute('BEGIN')
conn.execute('ALTER TABLE experiment_results RENAME TO experiment_results_old')
conn.execute("\nCREATE TABLE experiment_results (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    sample_id TEXT NOT NULL,\n    repo TEXT NOT NULL,\n    file_path TEXT NOT NULL,\n    function_name TEXT NOT NULL,\n    condition TEXT NOT NULL CHECK(condition IN ('K','T','A','G','C')),\n    cc_before REAL, mi_before REAL, loc_before INTEGER,\n    smell_count_before INTEGER,\n    tests_passed_before INTEGER, tests_total_before INTEGER,\n    mutation_score_before REAL,\n    cc_after REAL, mi_after REAL, loc_after INTEGER,\n    smell_count_after INTEGER,\n    tests_passed_after INTEGER, tests_total_after INTEGER,\n    mutation_score_after REAL,\n    patch_applied INTEGER DEFAULT 0,\n    patch_accepted INTEGER DEFAULT 0,\n    rejection_reason TEXT,\n    model_name TEXT,\n    tokens_in INTEGER, tokens_out INTEGER,\n    cost_usd REAL, response_time_s REAL,\n    refused INTEGER DEFAULT 0,\n    audit_log_path TEXT,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n)\n")
conn.execute('INSERT INTO experiment_results SELECT * FROM experiment_results_old')
conn.execute('DROP TABLE experiment_results_old')
conn.commit()
count = conn.execute("SELECT COUNT(*) FROM experiment_results WHERE condition='K'").fetchone()[0]
print(f'Migration OK. K rows preserved: {count}')
conn.close()
