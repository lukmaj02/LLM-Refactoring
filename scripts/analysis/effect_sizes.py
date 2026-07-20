from __future__ import annotations
from _dataio import ANALYSIS_DIR, load_v2, write_summary
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parent))
B_RESAMPLES = 10000
RNG = np.random.default_rng(42)


def cliffs_delta(a, b) -> dict:
    a = np.asarray([x for x in a if not pd.isna(x)])
    b = np.asarray([x for x in b if not pd.isna(x)])
    if len(a) == 0 or len(b) == 0:
        return {'n_a': int(len(a)), 'n_b': int(len(b)), 'cliffs_delta': None,
                'magnitude': None, 'A12': None}
    greater = sum((1 for x in a for y in b if x > y))
    less = sum((1 for x in a for y in b if x < y))
    total = len(a) * len(b)
    delta = (greater - less) / total
    A12 = (greater + 0.5 * (total - greater - less)) / total
    abs_d = abs(delta)
    if abs_d < 0.147:
        mag = 'negligible'
    elif abs_d < 0.33:
        mag = 'small'
    elif abs_d < 0.474:
        mag = 'medium'
    else:
        mag = 'large'
    return {'n_a': int(len(a)), 'n_b': int(len(b)), 'cliffs_delta': round(
        float(delta), 4), 'A12': round(float(A12), 4), 'magnitude': mag}


def bootstrap_median_ci(values, *, B: int = B_RESAMPLES) -> dict:
    import warnings
    s = np.asarray([v for v in values if not pd.isna(v)], dtype=float)
    if len(s) < 5:
        return {'n': int(len(s)), 'median': None, 'ci_low': None, 'ci_high': None, 'method': None}
    median = round(float(np.median(s)), 3)
    for method in ('BCa', 'percentile'):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error')
                res = stats.bootstrap((s,), np.median, confidence_level=0.95,
                                      n_resamples=B, method=method, random_state=RNG)
            lo, hi = (res.confidence_interval.low, res.confidence_interval.high)
            if np.isfinite(lo) and np.isfinite(hi):
                return {'n': int(len(s)), 'median': median, 'ci_low': round(
                    float(lo), 3), 'ci_high': round(float(hi), 3), 'method': method}
        except Exception:
            continue
    boot = RNG.choice(s, size=(B, len(s)), replace=True)
    medians = np.median(boot, axis=1)
    return {'n': int(len(s)), 'median': median, 'ci_low': round(float(np.percentile(medians, 2.5)), 3),
            'ci_high': round(float(np.percentile(medians, 97.5)), 3), 'method': 'percentile_manual'}


def per_condition_ci(df: pd.DataFrame, metric: str) -> dict:
    out: dict[str, dict] = {}
    for cond, sub in df.groupby('condition'):
        out[str(cond)] = bootstrap_median_ci(sub[metric].tolist())
    return out


def cliffs_vs_baseline(df: pd.DataFrame, metric: str, *, baseline: str = 'T') -> dict:
    out: dict[str, dict] = {}
    base = df[df['condition'] == baseline][metric].tolist()
    for cond in sorted(df['condition'].unique()):
        if cond == baseline:
            continue
        comp = df[df['condition'] == cond][metric].tolist()
        out[f'{cond}_vs_{baseline}'] = cliffs_delta(comp, base)
    return out


def render_md(payload: dict) -> str:
    md = ['# 5.3 Wielkosci efektow i bootstrap 95% CI dla median\n']
    md.append("Bootstrap BCa (B=10 000, scipy.stats.bootstrap). Cliff's delta kategoryzowany wg Romano et al. 2006: |d|<0.147 znikomy, <0.33 maly, <0.474 sredni, >=0.474 duzy.\n")
    for metric, ci_map in payload['bootstrap_median_ci'].items():
        md.append(f'## Bootstrap 95% CI dla median - {metric}\n')
        md.append('| condition | n | median | CI low | CI high | method |')
        md.append('|---|---|---|---|---|---|')
        for cond, ci in sorted(ci_map.items()):
            md.append(
                f"| {cond} | {ci.get('n', '-')} | {ci.get('median', '-')} | {ci.get('ci_low', '-')} | {ci.get('ci_high', '-')} | {ci.get('method', '-')} |")
        md.append('')
    for metric, cmp in payload['cliffs_vs_T'].items():
        md.append(f"## Cliff's delta vs T - {metric}\n")
        md.append('| comparison | n_a | n_b | Cliff d | A12 | magnitude |')
        md.append('|---|---|---|---|---|---|')
        for key, r in cmp.items():
            md.append(
                f"| {key} | {r['n_a']} | {r['n_b']} | {r['cliffs_delta']} | {r['A12']} | {r['magnitude']} |")
        md.append('')
    return '\n'.join(md) + '\n'


def run() -> dict:
    v2 = load_v2(applied_only=True)
    metrics = ['delta_cc', 'delta_mi', 'quality_score', 'pass_ratio']
    payload = {'bootstrap_median_ci': {}, 'cliffs_vs_T': {}}
    for m in metrics:
        if m in v2.columns:
            payload['bootstrap_median_ci'][m] = per_condition_ci(v2, m)
            payload['cliffs_vs_T'][m] = cliffs_vs_baseline(v2, m, baseline='T')
    write_summary('effect_sizes', payload)
    out_md = ANALYSIS_DIR / 'effect_sizes.md'
    out_md.write_text(render_md(payload), encoding='utf-8')
    print(f"[effect_sizes] summary -> {ANALYSIS_DIR / 'effect_sizes.json'}")
    print(f'[effect_sizes] report  -> {out_md}')
    return payload


if __name__ == '__main__':
    run()
