from __future__ import annotations
import json
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
SNAPSHOT_DIR = ROOT / 'data' / 'snapshots'
REFACTORED_DIR = ROOT / 'data' / 'refactored_v2'
AUDIT_DIR = ROOT / 'logs' / 'faza_4c'
OUT_PATH = ROOT / 'docs' / 'thesis_case_studies.json'
CBB_SAMPLE = 'flask_001'
CBB_COND = 'A'


def _tests_green(row: sqlite3.Row) -> bool:
    return (row['tests_targeted'] or 0) > 0 and (row['tests_failed'] or 0) == 0 and (
        (row['tests_errors'] or 0) == 0) and ((row['tests_timeout'] or 0) == 0) and ((row['tests_passed'] or 0) > 0)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d['delta_cc'] = (row['cc_before'] or 0) - (row['cc_after'] or 0)
    d['tests_green_strict'] = int(_tests_green(row))
    d['snapshot_path'] = str(SNAPSHOT_DIR / f"{row['sample_id']}.py")
    d['refactored_path'] = str(REFACTORED_DIR / f"{row['sample_id']}_{row['condition']}.py")
    audit = AUDIT_DIR / f"audit_{row['sample_id']}_{row['condition']}.json"
    d['audit_path'] = str(audit) if audit.exists() else None
    return d


def pick_success(conn: sqlite3.Connection) -> dict:
    cur = conn.execute("\n        SELECT * FROM experiment_results_v2\n        WHERE phase='4C' AND patch_applied=1\n          AND tests_targeted > 0 AND tests_failed = 0\n          AND tests_errors = 0 AND tests_timeout = 0\n          AND tests_passed > 0\n          AND cc_before IS NOT NULL AND cc_after IS NOT NULL\n          AND (cc_before - cc_after) >= 3\n          AND repo != 'flask'\n        ORDER BY (cc_before - cc_after) DESC, quality_score DESC\n        LIMIT 1\n        ")
    row = cur.fetchone()
    if row is None:
        cur = conn.execute("\n            SELECT * FROM experiment_results_v2\n            WHERE phase='4C' AND patch_applied=1\n              AND tests_targeted > 0 AND tests_failed = 0\n              AND tests_errors = 0 AND tests_timeout = 0\n              AND tests_passed > 0\n            ORDER BY (cc_before - cc_after) DESC\n            LIMIT 1\n            ")
        row = cur.fetchone()
    if row is None:
        raise RuntimeError('No success case found in experiment_results_v2')
    return _row_to_dict(row)


def pick_cbb(conn: sqlite3.Connection) -> dict:
    cur = conn.execute(
        "\n        SELECT * FROM experiment_results_v2\n        WHERE phase='4C' AND sample_id=? AND condition=?\n        ",
        (CBB_SAMPLE,
         CBB_COND))
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f'CBB case {CBB_SAMPLE}_{CBB_COND} not in DB')
    return _row_to_dict(row)


def load_audit_summary(path: str | None) -> dict | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding='utf-8'))
    return {'model_name': data.get('model_name'), 'changed_pct': data.get('changed_pct'), 'rejection_reason': data.get(
        'rejection_reason'), 'tests': data.get('tests'), 'quality': data.get('quality')}


def main() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    success = pick_success(conn)
    cbb = pick_cbb(conn)
    conn.close()
    out = {
        'success': {
            **success,
            'audit_summary': load_audit_summary(
                success.get('audit_path'))},
        'compile_but_break': {
            **cbb,
            'audit_summary': load_audit_summary(
                cbb.get('audit_path'))},
        'illustration_sample': cbb['sample_id'],
        'illustration_condition': cbb['condition']}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Wrote {OUT_PATH}')
    print(f"  success: {success['sample_id']} x {success['condition']} ({success['repo']})")
    print(f"  cbb:     {cbb['sample_id']} x {cbb['condition']} ({cbb['repo']})")


if __name__ == '__main__':
    main()
