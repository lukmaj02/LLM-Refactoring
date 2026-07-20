from __future__ import annotations
import json
import sqlite3
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
ANALYSIS_DIR = ROOT / 'results' / 'analysis'
FIGURES_DIR = ANALYSIS_DIR / 'figures'


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_v1(*, applied_only: bool = False) -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query('SELECT * FROM experiment_results', conn)
    df['delta_cc'] = df['cc_before'] - df['cc_after']
    df['delta_mi'] = df['mi_after'] - df['mi_before']
    df['source'] = 'v1'
    if applied_only:
        df = df[df['patch_applied'] == 1].copy()
    return df


def load_v2(*, applied_only: bool = False, with_tests: bool = False) -> pd.DataFrame:
    with _connect() as conn:
        df = pd.read_sql_query("SELECT * FROM experiment_results_v2 WHERE phase='4C'", conn)
    df['delta_cc'] = df['cc_before'] - df['cc_after']
    df['delta_mi'] = df['mi_after'] - df['mi_before']
    df['tests_total'] = df['tests_passed'].fillna(
        0) + df['tests_failed'].fillna(0) + df['tests_errors'].fillna(0)
    df['pass_ratio'] = df.apply(lambda r: r['tests_passed'] /
                                r['tests_total'] if r['tests_total'] > 0 else None, axis=1)
    df['tests_green_strict'] = (
        (df['tests_passed'].fillna(0) > 0) & (
            df['tests_failed'].fillna(0) == 0) & (
            df['tests_errors'].fillna(0) == 0) & (
                df['tests_timeout'].fillna(0) == 0)).astype(int)
    df['tests_green_relaxed'] = (
        (df['tests_passed'].fillna(0) > 0) & (
            df['tests_failed'].fillna(0) <= 1) & (
            df['tests_errors'].fillna(0) == 0) & (
                df['tests_timeout'].fillna(0) == 0)).astype(int)
    df['source'] = 'v2'
    if applied_only:
        df = df[df['patch_applied'] == 1].copy()
    if with_tests:
        df = df[df['tests_targeted'].fillna(0) > 0].copy()
    return df


def load_snapshot_index() -> pd.DataFrame:
    idx_path = ROOT / 'data' / 'snapshots' / 'index.json'
    with idx_path.open('r', encoding='utf-8') as fh:
        return pd.DataFrame(json.load(fh))


def paired_table_v2(df: pd.DataFrame, *,
                    conditions: tuple[str, ...] = ('T', 'A', 'G', 'C')) -> pd.DataFrame:
    pivot = df.pivot_table(index='sample_id', columns='condition', values='delta_cc')
    return pivot[[c for c in conditions if c in pivot.columns]]


def write_summary(name: str, payload: dict) -> Path:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    p = ANALYSIS_DIR / f'{name}.json'
    p.write_text(json.dumps(payload, indent=2, default=str), encoding='utf-8')
    return p
