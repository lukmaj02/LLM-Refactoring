from __future__ import annotations
from _dataio import FIGURES_DIR, load_v1, load_v2
import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
matplotlib.use('Agg')
matplotlib.rcParams.update({'font.family': 'DejaVu Sans',
                            'font.size': 11,
                            'axes.titlesize': 13,
                            'axes.labelsize': 12,
                            'xtick.labelsize': 10,
                            'ytick.labelsize': 10,
                            'legend.fontsize': 10,
                            'figure.dpi': 100,
                            'savefig.dpi': 300,
                            'savefig.bbox': 'tight'})
sys.path.insert(0, str(Path(__file__).resolve().parent))
COND_LABELS = {
    'T': 'T\n(autopep8)',
    'A': 'A\nGPT-4o',
    'G': 'G\nGemini 2.5',
    'C': 'C\nClaude S.4.6',
    'K': 'K\n(kontrolny)'}
COND_ORDER = ('T', 'A', 'G', 'C')
COND_COLORS = {'T': '#888888', 'A': '#1f77b4', 'G': '#2ca02c', 'C': '#d62728', 'K': '#cccccc'}


def _box_data(df: pd.DataFrame, metric: str):
    data, labels, colors = ([], [], [])
    for c in COND_ORDER:
        s = df[df['condition'] == c][metric].dropna()
        if len(s) == 0:
            continue
        data.append(s.values)
        labels.append(f'{COND_LABELS[c]}\nn={len(s)}')
        colors.append(COND_COLORS[c])
    return (data, labels, colors)


def fig_delta_cc_box(v2: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(7, 5))
    data, labels, colors = _box_data(v2, 'delta_cc')
    bp = ax.boxplot(
        data,
        labels=labels,
        patch_artist=True,
        widths=0.6,
        showmeans=True,
        meanprops={
            'marker': 'D',
            'markerfacecolor': 'yellow',
            'markeredgecolor': 'black',
            'markersize': 6})
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(1.6)
    ax.axhline(0, linestyle=':', color='grey', linewidth=0.8)
    ax.set_ylabel('ΔCC = CC_before − CC_after')
    ax.set_title('Redukcja złożoności cyklomatycznej (Faza 4C)')
    ax.grid(axis='y', alpha=0.3)
    out = FIGURES_DIR / 'fig_delta_cc_box.png'
    fig.savefig(out)
    plt.close(fig)
    return out


def fig_pass_ratio_box(v2: pd.DataFrame) -> Path:
    sub = v2[v2['pass_ratio'].notna()]
    fig, ax = plt.subplots(figsize=(7, 5))
    data, labels, colors = _box_data(sub, 'pass_ratio')
    bp = ax.boxplot(
        data,
        labels=labels,
        patch_artist=True,
        widths=0.6,
        showmeans=True,
        meanprops={
            'marker': 'D',
            'markerfacecolor': 'yellow',
            'markeredgecolor': 'black',
            'markersize': 6})
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.5)
    for median in bp['medians']:
        median.set_color('black')
        median.set_linewidth(1.6)
    ax.axhline(1.0, linestyle=':', color='grey', linewidth=0.8, label='100% testów zielonych')
    ax.set_ylabel('Pass ratio (passed / total)')
    ax.set_title('Faktyczny wskaźnik powodzenia testów (Faza 4C)')
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc='lower left')
    ax.grid(axis='y', alpha=0.3)
    out = FIGURES_DIR / 'fig_pass_ratio_box.png'
    fig.savefig(out)
    plt.close(fig)
    return out


def fig_judge_vs_tests(v2: pd.DataFrame) -> Path:
    sub = v2[v2['pass_ratio'].notna() & v2['quality_score'].notna()].copy()
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    for c in COND_ORDER:
        s = sub[sub['condition'] == c]
        if s.empty:
            continue
        ax.scatter(s['quality_score'] + np.random.uniform(-0.1,
                                                          0.1,
                                                          len(s)),
                   s['pass_ratio'] + np.random.uniform(-0.005,
                                                       0.005,
                                                       len(s)),
                   c=COND_COLORS[c],
                   alpha=0.55,
                   s=32,
                   label=f'{c} (n={len(s)})',
                   edgecolor='white',
                   linewidth=0.4)
    rho, p = stats.spearmanr(sub['quality_score'], sub['pass_ratio'])
    ax.set_xlabel('Quality score (LLM-judge)')
    ax.set_ylabel('Pass ratio (pytest)')
    ax.set_title(
        f'Kluczowy wynik: LLM-judge NIE koreluje z faktyczną poprawnością\nSpearman ρ = {rho:.3f}, p = {p:.3f}, n = {len(sub)}')
    ax.legend(title='Warunek', loc='lower left')
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.3)
    out = FIGURES_DIR / 'fig_judge_vs_tests.png'
    fig.savefig(out)
    plt.close(fig)
    return out


def fig_judge_bias_changed_pct(v2: pd.DataFrame) -> Path:
    sub = v2[v2['changed_pct'].notna() & v2['quality_score'].notna() &
             v2['condition'].isin(['A', 'G', 'C'])].copy()
    fig, ax = plt.subplots(figsize=(7.5, 5.5))
    for c in ('A', 'G', 'C'):
        s = sub[sub['condition'] == c]
        if s.empty:
            continue
        ax.scatter(s['changed_pct'],
                   s['quality_score'] + np.random.uniform(-0.15,
                                                          0.15,
                                                          len(s)),
                   c=COND_COLORS[c],
                   alpha=0.55,
                   s=32,
                   label=f'{c} (n={len(s)})',
                   edgecolor='white',
                   linewidth=0.4)
    if len(sub) > 5:
        coef = np.polyfit(sub['changed_pct'], sub['quality_score'], 1)
        x = np.linspace(0, 1, 50)
        ax.plot(x, np.polyval(coef, x), 'k--', linewidth=1.4,
                label=f'trend (y = {coef[0]:.1f}·x + {coef[1]:.1f})')
    rho, p = stats.spearmanr(sub['changed_pct'], sub['quality_score'])
    ax.set_xlabel('Changed pct (frakcja zmienionych linii)')
    ax.set_ylabel('Quality score (LLM-judge)')
    ax.set_title(
        f'Bias LLM-judge: ocena rośnie z rozmiarem zmiany, nie poprawnością\nSpearman ρ = {rho:.3f}, p = {p:.3g}, n = {len(sub)}')
    ax.legend(loc='lower right')
    ax.set_ylim(-0.5, 10.5)
    ax.grid(alpha=0.3)
    out = FIGURES_DIR / 'fig_judge_bias_changed_pct.png'
    fig.savefig(out)
    plt.close(fig)
    return out


def fig_accept_rate_v1_v2(v1: pd.DataFrame, v2: pd.DataFrame) -> Path:
    conds = ('T', 'A', 'G', 'C')
    rates_v1, rates_v2 = ([], [])
    n_v1, n_v2 = ([], [])
    for c in conds:
        s1 = v1[v1['condition'] == c]
        s2 = v2[v2['condition'] == c]
        rates_v1.append(float(s1['patch_accepted'].sum()) / len(s1) if len(s1) else 0)
        rates_v2.append(float(s2['patch_accepted'].sum()) / len(s2) if len(s2) else 0)
        n_v1.append(len(s1))
        n_v2.append(len(s2))
    x = np.arange(len(conds))
    w = 0.38
    fig, ax = plt.subplots(figsize=(8, 5))
    b1 = ax.bar(
        x - w / 2,
        rates_v1,
        w,
        label='v1 (Fazy 4+4B, bez bramki testowej)',
        color='#1f77b4',
        alpha=0.85,
        edgecolor='white')
    b2 = ax.bar(
        x + w / 2,
        rates_v2,
        w,
        label='v2 (Faza 4C, z bramką testową)',
        color='#d62728',
        alpha=0.85,
        edgecolor='white')
    for bar, rate, n in zip(b1, rates_v1, n_v1):
        ax.text(
            bar.get_x() +
            bar.get_width() /
            2,
            rate +
            0.015,
            f'{rate * 100:.1f}%\nn={n}',
            ha='center',
            fontsize=9)
    for bar, rate, n in zip(b2, rates_v2, n_v2):
        ax.text(
            bar.get_x() +
            bar.get_width() /
            2,
            rate +
            0.015,
            f'{rate * 100:.1f}%\nn={n}',
            ha='center',
            fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels([COND_LABELS[c].replace('\n', ' ') for c in conds])
    ax.set_ylabel('Accept rate (frakcja zaakceptowanych łatek)')
    ax.set_title('Wpływ dodania faktycznej walidacji testowej na wskaźnik akceptacji')
    ax.set_ylim(0, max(max(rates_v1), max(rates_v2)) * 1.25 + 0.05)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    out = FIGURES_DIR / 'fig_accept_rate_v1_v2.png'
    fig.savefig(out)
    plt.close(fig)
    return out


def fig_quality_dimensions(v2: pd.DataFrame) -> Path:
    dims = [('solid_score', 'SOLID'), ('dry_score', 'DRY'), ('kiss_score', 'KISS'),
            ('semantic_score', 'Semantic\nEquivalence'), ('quality_score', 'Overall\nQuality')]
    conds = COND_ORDER
    x = np.arange(len(dims))
    w = 0.2
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for i, c in enumerate(conds):
        means = []
        for col, _ in dims:
            s = v2[v2['condition'] == c][col].dropna()
            means.append(float(s.mean()) if len(s) else 0)
        offset = (i - (len(conds) - 1) / 2) * w
        bars = ax.bar(
            x + offset,
            means,
            w,
            label=c,
            color=COND_COLORS[c],
            alpha=0.85,
            edgecolor='white')
        for bar, m in zip(bars, means):
            ax.text(
                bar.get_x() +
                bar.get_width() /
                2,
                m +
                0.15,
                f'{m:.1f}',
                ha='center',
                fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in dims])
    ax.set_ylabel('Średnia ocena LLM-judge (0–10)')
    ax.set_title('Oceny LLM-judge w pięciu wymiarach (Faza 4C)')
    ax.set_ylim(0, 11)
    ax.axhline(8, linestyle=':', color='grey', linewidth=0.8, label='Próg semantic = 8')
    ax.legend(loc='lower right', ncol=2)
    ax.grid(axis='y', alpha=0.3)
    out = FIGURES_DIR / 'fig_quality_dimensions.png'
    fig.savefig(out)
    plt.close(fig)
    return out


def run() -> dict:
    v1 = load_v1()
    v2 = load_v2(applied_only=True)
    np.random.seed(42)
    outputs = {
        'delta_cc_box': fig_delta_cc_box(v2),
        'pass_ratio_box': fig_pass_ratio_box(v2),
        'judge_vs_tests': fig_judge_vs_tests(v2),
        'judge_bias_changed_pct': fig_judge_bias_changed_pct(v2),
        'accept_rate_v1_v2': fig_accept_rate_v1_v2(
            v1,
            v2),
        'quality_dimensions': fig_quality_dimensions(v2)}
    for name, path in outputs.items():
        print(f'[fig] {name}: {path}')
    return {k: str(v) for k, v in outputs.items()}


if __name__ == '__main__':
    run()
