from __future__ import annotations
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
SCHEMA = "\nCREATE TABLE IF NOT EXISTS experiment_results (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    sample_id TEXT NOT NULL,\n    repo TEXT NOT NULL,\n    file_path TEXT NOT NULL,\n    function_name TEXT NOT NULL,\n    condition TEXT NOT NULL CHECK(condition IN ('K','T','A','G','C')),\n    cc_before REAL, mi_before REAL, loc_before INTEGER,\n    smell_count_before INTEGER,\n    tests_passed_before INTEGER, tests_total_before INTEGER,\n    mutation_score_before REAL,\n    cc_after REAL, mi_after REAL, loc_after INTEGER,\n    smell_count_after INTEGER,\n    tests_passed_after INTEGER, tests_total_after INTEGER,\n    mutation_score_after REAL,\n    patch_applied INTEGER DEFAULT 0,\n    patch_accepted INTEGER DEFAULT 0,\n    rejection_reason TEXT,\n    model_name TEXT,\n    tokens_in INTEGER, tokens_out INTEGER,\n    cost_usd REAL, response_time_s REAL,\n    refused INTEGER DEFAULT 0,\n    audit_log_path TEXT,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n);\n\nCREATE TABLE IF NOT EXISTS pipeline_runs (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    repo TEXT NOT NULL,\n    commit_hash TEXT NOT NULL,\n    config TEXT NOT NULL CHECK(config IN ('baseline','arp')),\n    total_duration_s REAL,\n    arp_stage_duration_s REAL DEFAULT 0,\n    build_status TEXT,\n    failed_stage TEXT,\n    patches_generated INTEGER DEFAULT 0,\n    patches_accepted INTEGER DEFAULT 0,\n    patches_rejected INTEGER DEFAULT 0,\n    api_cost_usd REAL DEFAULT 0,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n);\n"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(SCHEMA)
    conn.close()
    conn = sqlite3.connect(str(DB_PATH))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    conn.close()
    print(f'[init_db] Database created at {DB_PATH}')
    print(f'[init_db] Tables: {tables}')


if __name__ == '__main__':
    main()
