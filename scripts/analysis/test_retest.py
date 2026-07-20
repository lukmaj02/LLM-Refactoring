from __future__ import annotations
from _dataio import ANALYSIS_DIR, FIGURES_DIR, DB_PATH, write_summary
import sqlite3
import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score
matplotlib.use('Agg')
sys.path.insert(0, str(Path(__file__).resolve().parent))
DIMENSIONS = ('quality_score', 'solid_score', 'dry_score', 'kiss_score', 'semantic_score')


def load_paired() -> pd.DataFrame:
    cols = ', '.join(DIMENSIONS)
    with sqlite3.connect(str(DB_PATH)) as conn:
        v1 = pd.read_sql_query(
            f'SELECT sample_id, condition, {cols} FROM experiment_results WHERE patch_applied=1', conn)
        v2 = pd.read_sql_query(
            f"SELECT sample_id, condition, {cols} FROM experiment_results_v2 WHERE patch_applied=1 AND phase='4C'",
            conn)
    merged = v1.merge(v2, on=['sample_id', 'condition'], suffixes=('_v1', '_v2'))
    return merged


def icc_2_1(x: np.ndarray, y: np.ndarray) -> dict:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = ~np.isnan(x) & ~np.isnan(y)
    x, y = (x[mask], y[mask])
    n = len(x)
    if n < 5:
        return {'n': int(n), 'icc': None, 'ci_low': None, 'ci_high': None}
    k = 2
    ratings = np.stack([x, y], axis=1)
    mean_per_subject = ratings.mean(axis=1)
    mean_per_rater = ratings.mean(axis=0)
    grand_mean = ratings.mean()
    ss_total = ((ratings - grand_mean) ** 2).sum()
    ss_between_subjects = k * ((mean_per_subject - grand_mean) ** 2).sum()
    ss_between_raters = n * ((mean_per_rater - grand_mean) ** 2).sum()
    ss_residual = ss_total - ss_between_subjects - ss_between_raters
    ms_between_subjects = ss_between_subjects / (n - 1)
    ms_between_raters = ss_between_raters / (k - 1)
    ms_residual = ss_residual / ((n - 1) * (k - 1))
    icc = (ms_between_subjects - ms_residual) / (ms_between_subjects +
                                                 (k - 1) * ms_residual + k * (ms_between_raters - ms_residual) / n)
    f_value = ms_between_subjects / ms_residual if ms_residual > 0 else np.nan
    df1 = n - 1
    df2 = (n - 1) * (k - 1)
    alpha = 0.05
    f_low = stats.f.ppf(1 - alpha / 2, df1, df2)
    f_high = stats.f.ppf(alpha / 2, df1, df2)
    if f_high > 0 and f_low > 0 and (not np.isnan(f_value)):
        lower_f = f_value / f_low
        upper_f = f_value / f_high
        ci_low = (lower_f - 1) / (lower_f + k - 1)
        ci_high = (upper_f - 1) / (upper_f + k - 1)
    else:
        ci_low = ci_high = np.nan
    return {'n': int(n), 'icc': round(float(icc), 4), 'ci_low': round(float(ci_low), 4) if not np.isnan(
        ci_low) else None, 'ci_high': round(float(ci_high), 4) if not np.isnan(ci_high) else None, 'interpretation': _icc_label(icc)}


def _icc_label(icc: float) -> str:
    if np.isnan(icc):
        return 'n/d'
    if icc < 0.5:
        return 'poor'
    if icc < 0.75:
        return 'moderate'
    if icc < 0.9:
        return 'good'
    return 'excellent'


def reliability_per_dim(merged: pd.DataFrame, dim: str) -> dict:
    v1 = merged[f'{dim}_v1'].to_numpy()
    v2 = merged[f'{dim}_v2'].to_numpy()
    mask = ~np.isnan(v1) & ~np.isnan(v2)
    v1, v2 = (v1[mask], v2[mask])
    if len(v1) < 5:
        return {'n': int(len(v1)), 'note': 'too few pairs'}
    rho, p = stats.spearmanr(v1, v2)
    diff = v2 - v1
    icc = icc_2_1(v1, v2)
    try:
        v1_int = np.round(v1).astype(int)
        v2_int = np.round(v2).astype(int)
        kappa_q = float(cohen_kappa_score(v1_int, v2_int, weights='quadratic'))
    except ValueError:
        kappa_q = None
    return {'n_pairs': int(len(v1)), 'spearman_rho': round(float(rho), 4), 'spearman_p': round(float(p), 6), 'icc_2_1': icc, 'kappa_quadratic': round(kappa_q, 4) if kappa_q is not None else None, 'mean_diff': round(float(np.mean(diff)), 3), 'mean_abs_diff': round(
        float(np.mean(np.abs(diff))), 3), 'sd_diff': round(float(np.std(diff, ddof=1)), 3), 'loa_lower': round(float(np.mean(diff) - 1.96 * np.std(diff, ddof=1)), 3), 'loa_upper': round(float(np.mean(diff) + 1.96 * np.std(diff, ddof=1)), 3)}


def bland_altman_plot(merged: pd.DataFrame, dim: str = 'quality_score') -> Path:
    v1 = merged[f'{dim}_v1'].to_numpy()
    v2 = merged[f'{dim}_v2'].to_numpy()
    mask = ~np.isnan(v1) & ~np.isnan(v2)
    v1, v2 = (v1[mask], v2[mask])
    means = (v1 + v2) / 2.0
    diffs = v2 - v1
    mean_d = float(np.mean(diffs))
    sd_d = float(np.std(diffs, ddof=1))
    loa_lo, loa_hi = (mean_d - 1.96 * sd_d, mean_d + 1.96 * sd_d)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(means + np.random.uniform(-0.1, 0.1, len(means)), diffs + np.random.uniform(-0.1,
               0.1, len(diffs)), alpha=0.45, s=30, color='#1f77b4', edgecolor='white', linewidth=0.4)
    ax.axhline(mean_d, color='black', linewidth=1.0, label=f'bias (v2-v1) = {mean_d:.2f}')
    ax.axhline(
        loa_hi,
        color='#d62728',
        linestyle='--',
        linewidth=1.0,
        label=f'+1.96 SD = {loa_hi:.2f}')
    ax.axhline(
        loa_lo,
        color='#d62728',
        linestyle='--',
        linewidth=1.0,
        label=f'-1.96 SD = {loa_lo:.2f}')
    ax.set_xlabel(f'Srednia ocena (v1 + v2) / 2 - {dim}')
    ax.set_ylabel('Roznica (v2 - v1)')
    ax.set_title(
        f'Bland-Altman: LLM-judge test-retest reliability ({dim})\nn={len(v1)}, bias={mean_d:+.2f}, LoA=[{loa_lo:.2f}, {loa_hi:.2f}]')
    ax.legend(loc='lower right')
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = FIGURES_DIR / f'fig_bland_altman_{dim}.png'
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def render_md(payload: dict) -> str:
    md = ['# 5.A3 Test-retest reliability LLM-as-Judge (v1 vs v2)\n']
    md.append(f"Spjety zbior: **{payload['n_pairs_total']}** par (sample_id, condition) obecnych jednoczesnie w v1 (Faza 4+4B, T=0.2) i v2 (Faza 4C, T=0.0). Dla kazdego z 5 wymiarow LLM-judge porownujemy ocene v1 z ocena v2 - **idealna reliability oznaczaloby wysoka zgodnosc**.\n")
    md.append('ICC interpretacja (Koo & Li 2016): <0.50 poor, 0.50-0.75 moderate, 0.75-0.90 good, >=0.90 excellent.\n')
    md.append('## Per-dimension reliability\n')
    md.append('| Dim | n_pairs | Spearman rho | p | ICC(2,1) | ICC 95% CI | Kappa (quad) | mean_diff (v2-v1) | LoA |')
    md.append('|---|---|---|---|---|---|---|---|---|')
    for dim, r in payload['dimensions'].items():
        if 'note' in r:
            md.append(f"| {dim} | {r['n_pairs']} | - | - | - | - | - | - | - |")
            continue
        icc = r['icc_2_1']
        md.append(f"| {dim} | {r['n_pairs']} | {r['spearman_rho']} | {r['spearman_p']} | {icc['icc']} ({icc['interpretation']}) | [{icc['ci_low']}, {icc['ci_high']}] | {r['kappa_quadratic']} | {r['mean_diff']} | [{r['loa_lower']}, {r['loa_upper']}] |")
    md.append('\n## Interpretacja\n')
    q = payload['dimensions'].get('quality_score', {})
    s = payload['dimensions'].get('semantic_score', {})
    if q and 'note' not in q:
        md.append(
            f"- **quality_score:** Spearman rho = {q['spearman_rho']}, ICC = {q['icc_2_1']['icc']} ({q['icc_2_1']['interpretation']}). Srednia bezwzgledna roznica miedzy v1 i v2 = {q['mean_abs_diff']} punktow na skali 0-10.\n")
    if s and 'note' not in s:
        md.append(
            f"- **semantic_score:** Spearman rho = {s['spearman_rho']}, ICC = {s['icc_2_1']['icc']} ({s['icc_2_1']['interpretation']}).\n")
    md.append('\n**Wniosek dla pracy magisterskiej:** wartosci ICC ponizej 0.75 (moderate/poor) oznaczaja, ze LLM-judge **nie jest reliable nawet wobec siebie samego**. Kazda korelacja uzywajaca quality_score jest osłabiona przez attenuation effect - prawdziwa korelacja moze byc wyzsza, ale szum pomiaru ja maskuje. Roznice miedzy v1 i v2 to w czesci tez wynik niedeterminizmu (T=0.2 vs T=0.0).\n')
    return '\n'.join(md) + '\n'


def run() -> dict:
    np.random.seed(42)
    merged = load_paired()
    payload = {
        'n_pairs_total': int(
            len(merged)),
        'per_condition': merged.groupby('condition').size().to_dict(),
        'dimensions': {}}
    for dim in DIMENSIONS:
        payload['dimensions'][dim] = reliability_per_dim(merged, dim)
    fig = bland_altman_plot(merged, dim='quality_score')
    payload['bland_altman_figure'] = str(fig)
    fig_sem = bland_altman_plot(merged, dim='semantic_score')
    payload['bland_altman_semantic'] = str(fig_sem)
    write_summary('test_retest', payload)
    out_md = ANALYSIS_DIR / 'test_retest.md'
    out_md.write_text(render_md(payload), encoding='utf-8')
    print(f"[retest] summary -> {ANALYSIS_DIR / 'test_retest.json'}")
    print(f'[retest] report  -> {out_md}')
    print(f'[retest] BA quality -> {fig}')
    print(f"\nPaired total: {payload['n_pairs_total']}")
    for dim in DIMENSIONS:
        d = payload['dimensions'][dim]
        if 'note' in d:
            continue
        print(
            f"  {dim:20s}: rho={d['spearman_rho']:.3f}, ICC={d['icc_2_1']['icc']:.3f} ({d['icc_2_1']['interpretation']}), mean_abs_diff={d['mean_abs_diff']:.2f}")
    return payload


if __name__ == '__main__':
    run()
