from __future__ import annotations
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
SCHEMA_V2 = "\nCREATE TABLE IF NOT EXISTS experiment_results_v2 (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n\n    sample_id TEXT NOT NULL,\n    repo TEXT NOT NULL,\n    file_path TEXT NOT NULL,\n    function_name TEXT NOT NULL,\n    condition TEXT NOT NULL CHECK(condition IN ('K','T','A','G','C')),\n\n    cc_before REAL,\n    mi_before REAL,\n    loc_before INTEGER,\n    cc_after REAL,\n    mi_after REAL,\n    loc_after INTEGER,\n\n    patch_applied INTEGER DEFAULT 0,\n    patch_accepted INTEGER DEFAULT 0,\n    rejection_reason TEXT,\n    changed_pct REAL,\n\n    model_name TEXT,\n    tokens_in INTEGER,\n    tokens_out INTEGER,\n    cost_usd REAL,\n    response_time_s REAL,\n    refused INTEGER DEFAULT 0,\n    audit_log_path TEXT,\n\n    refactored_code_path TEXT,\n    refactored_code_hash TEXT,\n    prompt_with_context INTEGER DEFAULT 1,\n    temperature REAL DEFAULT 0.0,\n\n    tests_targeted INTEGER,\n    tests_run INTEGER,\n    tests_passed INTEGER,\n    tests_failed INTEGER,\n    tests_errors INTEGER,\n    tests_timeout INTEGER DEFAULT 0,\n    tests_duration_s REAL,\n    tests_selection_method TEXT,\n\n    solid_score INTEGER,\n    dry_score INTEGER,\n    kiss_score INTEGER,\n    semantic_score INTEGER,\n    quality_score INTEGER,\n    quality_rationale TEXT,\n    judge_called_on_path TEXT,\n\n    phase TEXT DEFAULT '4C',\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,\n\n    UNIQUE(sample_id, condition, phase)\n);\n\nCREATE INDEX IF NOT EXISTS idx_v2_sample_cond\n    ON experiment_results_v2 (sample_id, condition);\n\nCREATE INDEX IF NOT EXISTS idx_v2_repo_cond\n    ON experiment_results_v2 (repo, condition);\n"


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.executescript(SCHEMA_V2)
        conn.commit()
        cols = [r[1] for r in conn.execute('PRAGMA table_info(experiment_results_v2)').fetchall()]
    finally:
        conn.close()
    print(f'[init_db_v2] Database: {DB_PATH}')
    print(f'[init_db_v2] experiment_results_v2: {len(cols)} columns')
    print(f"[init_db_v2] Columns: {', '.join(cols)}")


if __name__ == '__main__':
    main()
