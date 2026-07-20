from __future__ import annotations
from _dataio import FIGURES_DIR, ANALYSIS_DIR, load_v1, load_v2, write_summary
import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
matplotlib.use('Agg')
sys.path.insert(0, str(Path(__file__).resolve().parent))
METRICS = ('delta_cc', 'delta_mi', 'quality_score')
METRIC_LABELS = {
    'delta_cc': 'ΔCC (cc_before − cc_after)',
    'delta_mi': 'ΔMI (mi_after − mi_before)',
    'quality_score': 'Quality score (LLM-judge, 0–10)',
    'pass_ratio': 'Pass ratio (testy)',
    'changed_pct': 'Changed pct'}


def _shapiro(series: pd.Series) -> dict:
    s = series.dropna()
    if len(s) < 3 or s.nunique() < 2:
        return {'n': int(len(s)), 'W': None, 'p': None, 'normal': None}
    try:
        W, p = stats.shapiro(s)
    except ValueError:
        return {'n': int(len(s)), 'W': None, 'p': None, 'normal': None}
    return {'n': int(len(s)), 'W': round(float(W), 4),
            'p': round(float(p), 6), 'normal': bool(p > 0.05)}


def _describe(series: pd.Series) -> dict:
    s = series.dropna()
    if s.empty:
        return {'n': 0}
    return {'n': int(len(s)), 'mean': round(float(s.mean()), 3), 'median': round(float(s.median()), 3), 'std': round(float(s.std(ddof=1)), 3), 'min': round(float(s.min()), 3), 'q25': round(
        float(s.quantile(0.25)), 3), 'q75': round(float(s.quantile(0.75)), 3), 'max': round(float(s.max()), 3), 'iqr': round(float(s.quantile(0.75) - s.quantile(0.25)), 3)}


def per_condition_stats(df: pd.DataFrame, metric: str) -> dict:
    out: dict[str, dict] = {}
    for cond, sub in df.groupby('condition'):
        out[str(cond)] = {'describe': _describe(sub[metric]), 'shapiro': _shapiro(sub[metric])}
    return out


def render_md_table(per_cond: dict[str, dict], metric: str) -> str:
    rows = [f'### {METRIC_LABELS.get(metric, metric)}\n']
    rows.append('| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |')
    rows.append('|---|---|---|---|---|---|---|---|---|')
    for cond, payload in sorted(per_cond.items()):
        d = payload['describe']
        sh = payload['shapiro']
        if d.get('n', 0) == 0:
            continue
        rows.append(
            f"| {cond} | {d['n']} | {d['mean']} | {d['median']} | {d['std']} | {d['iqr']} | {sh['W']} | {sh['p']} | {('tak' if sh['normal'] else 'nie' if sh['normal'] is False else '-')} |")
    return '\n'.join(rows) + '\n'


def plot_histograms(df: pd.DataFrame, metric: str, *, source: str) -> Path:
    conds = sorted([c for c in df['condition'].dropna().unique()])
    fig, axes = plt.subplots(1, len(conds), figsize=(3.2 * len(conds), 3.4), sharey=True)
    if len(conds) == 1:
        axes = [axes]
    for ax, cond in zip(axes, conds):
        s = df[df['condition'] == cond][metric].dropna()
        if len(s) == 0:
            ax.set_title(f'{cond} (brak danych)')
            continue
        ax.hist(s, bins=min(20, max(5, len(s) // 4)),
                color='#4C72B0', edgecolor='white', alpha=0.85)
        ax.axvline(
            s.median(),
            color='#C44E52',
            linestyle='--',
            linewidth=1.2,
            label=f'med={s.median():.2f}')
        ax.set_title(f'{cond} (n={len(s)})', fontsize=11)
        ax.set_xlabel(METRIC_LABELS.get(metric, metric), fontsize=9)
        ax.tick_params(labelsize=9)
        ax.legend(fontsize=8, loc='upper right')
    axes[0].set_ylabel('Liczba próbek', fontsize=10)
    fig.suptitle(f'Rozkład: {METRIC_LABELS.get(metric, metric)} ({source})', fontsize=12)
    fig.tight_layout()
    out = FIGURES_DIR / f'eda_hist_{source}_{metric}.png'
    fig.savefig(out, dpi=180, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_qq(df: pd.DataFrame, metric: str, *, source: str) -> Path:
    conds = sorted([c for c in df['condition'].dropna().unique()])
    fig, axes = plt.subplots(1, len(conds), figsize=(3.2 * len(conds), 3.4))
    if len(conds) == 1:
        axes = [axes]
    for ax, cond in zip(axes, conds):
        s = df[df['condition'] == cond][metric].dropna()
        if len(s) < 3:
            ax.set_title(f'{cond} (n<3)')
            continue
        stats.probplot(s, dist='norm', plot=ax)
        ax.set_title(f'{cond} (n={len(s)})', fontsize=11)
        ax.tick_params(labelsize=8)
        ax.get_lines()[0].set_markersize(3)
        ax.get_lines()[0].set_color('#4C72B0')
        ax.get_lines()[1].set_color('#C44E52')
    fig.suptitle(f'Q-Q plot: {METRIC_LABELS.get(metric, metric)} ({source})', fontsize=12)
    fig.tight_layout()
    out = FIGURES_DIR / f'eda_qq_{source}_{metric}.png'
    fig.savefig(out, dpi=180, bbox_inches='tight')
    plt.close(fig)
    return out


def run() -> dict:
    v1 = load_v1(applied_only=True)
    v2 = load_v2(applied_only=True)
    summary: dict = {'v1': {}, 'v2': {}, 'figures': []}
    for metric in METRICS + ('changed_pct',):
        if metric in v1.columns:
            stats_v1 = per_condition_stats(v1, metric)
            summary['v1'][metric] = stats_v1
            fig = plot_histograms(v1, metric, source='v1')
            summary['figures'].append(str(fig.relative_to(ANALYSIS_DIR.parent.parent)))
            qq = plot_qq(v1, metric, source='v1')
            summary['figures'].append(str(qq.relative_to(ANALYSIS_DIR.parent.parent)))
    for metric in METRICS + ('changed_pct', 'pass_ratio'):
        if metric in v2.columns:
            stats_v2 = per_condition_stats(v2, metric)
            summary['v2'][metric] = stats_v2
            fig = plot_histograms(v2, metric, source='v2')
            summary['figures'].append(str(fig.relative_to(ANALYSIS_DIR.parent.parent)))
            qq = plot_qq(v2, metric, source='v2')
            summary['figures'].append(str(qq.relative_to(ANALYSIS_DIR.parent.parent)))
    write_summary('eda_summary', summary)
    md_parts = ['# 5.1 EDA - Statystyki opisowe i test normalnosci\n']
    md_parts.append('Statystyki obliczone na lacie poprawnych skladniowo refaktoryzacji (`patch_applied=1`). Test Shapiro-Wilka: H0 = rozklad normalny; p > 0,05 nie pozwala odrzucic H0.\n')
    md_parts.append('## Dane z v1 (Fazy 4 + 4B)\n')
    for metric, payload in summary['v1'].items():
        md_parts.append(render_md_table(payload, metric))
    md_parts.append('\n## Dane z v2 (Faza 4C)\n')
    for metric, payload in summary['v2'].items():
        md_parts.append(render_md_table(payload, metric))
    out = ANALYSIS_DIR / 'eda_report.md'
    out.write_text('\n'.join(md_parts), encoding='utf-8')
    print(f"[eda] summary -> {ANALYSIS_DIR / 'eda_summary.json'}")
    print(f'[eda] report  -> {out}')
    print(f"[eda] figures: {len(summary['figures'])} files in {FIGURES_DIR}")
    return summary


if __name__ == '__main__':
    run()
