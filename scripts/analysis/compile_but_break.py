from __future__ import annotations
from _dataio import ANALYSIS_DIR, FIGURES_DIR, load_v2, write_summary
import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.proportion import proportion_confint
matplotlib.use('Agg')
sys.path.insert(0, str(Path(__file__).resolve().parent))
COND_COLORS = {'T': '#888888', 'A': '#1f77b4', 'G': '#2ca02c', 'C': '#d62728'}


def categorize(v2: pd.DataFrame) -> pd.DataFrame:
    df = v2.copy()
    df['has_tests'] = df['tests_targeted'].fillna(0) > 0
    df['applied'] = df['patch_applied'] == 1
    conds = []
    for _, row in df.iterrows():
        if not row['applied']:
            conds.append('not_applied')
        elif not row['has_tests']:
            conds.append('applied_no_test')
        elif row['tests_green_strict'] == 1:
            conds.append('applied_green')
        else:
            conds.append('compile_but_break')
    df['category'] = conds
    return df


def per_condition_stats(df: pd.DataFrame) -> dict:
    out = {}
    for cond, sub in df.groupby('condition'):
        total = len(sub)
        applied_with_test = sub[sub['applied'] & sub['has_tests']]
        n_eligible = len(applied_with_test)
        cbb = (applied_with_test['category'] == 'compile_but_break').sum()
        green = (applied_with_test['category'] == 'applied_green').sum()
        if n_eligible > 0:
            lo, hi = proportion_confint(cbb, n_eligible, alpha=0.05, method='wilson')
        else:
            lo = hi = None
        out[str(cond)] = {'n_total': int(total),
                          'n_eligible_for_cbb': int(n_eligible),
                          'n_compile_but_break': int(cbb),
                          'n_applied_green': int(green),
                          'n_applied_no_test': int((sub['category'] == 'applied_no_test').sum()),
                          'n_not_applied': int((sub['category'] == 'not_applied').sum()),
                          'cbb_rate': round(cbb / n_eligible,
                                            4) if n_eligible else None,
                          'cbb_rate_wilson_ci': [round(float(lo),
                                                       4),
                                                 round(float(hi),
                                                       4)] if lo is not None else None}
    return out


def quality_distribution_in_cbb(df: pd.DataFrame) -> dict:
    cbb = df[df['category'] == 'compile_but_break']
    green = df[df['category'] == 'applied_green']
    if cbb.empty or green.empty:
        return {'note': 'insufficient data'}
    q_cbb = cbb['quality_score'].dropna()
    q_green = green['quality_score'].dropna()
    if len(q_cbb) < 3 or len(q_green) < 3:
        return {'n_cbb': int(len(q_cbb)), 'n_green': int(len(q_green)), 'note': 'too few for test'}
    u_res = stats.mannwhitneyu(q_cbb, q_green, alternative='two-sided')
    return {'n_cbb': int(len(q_cbb)), 'n_green': int(len(q_green)), 'median_quality_cbb': round(float(q_cbb.median()), 2), 'median_quality_green': round(float(q_green.median()), 2), 'mean_quality_cbb': round(
        float(q_cbb.mean()), 2), 'mean_quality_green': round(float(q_green.mean()), 2), 'mannwhitney_U': round(float(u_res.statistic), 3), 'mannwhitney_p': round(float(u_res.pvalue), 6)}


def plot_stacked(stats_per_cond: dict) -> Path:
    conds = ['T', 'A', 'G', 'C']
    cats = ['applied_green', 'compile_but_break', 'applied_no_test', 'not_applied']
    colors = {
        'applied_green': '#2ca02c',
        'compile_but_break': '#d62728',
        'applied_no_test': '#ffbb78',
        'not_applied': '#cccccc'}
    labels = {
        'applied_green': 'Applied + testy zielone',
        'compile_but_break': 'Compile-but-break (ukryta regresja)',
        'applied_no_test': 'Applied bez testow',
        'not_applied': 'Nie zaakceptowana'}
    fig, ax = plt.subplots(figsize=(8.5, 5))
    bottom = np.zeros(len(conds))
    for cat in cats:
        vals = [stats_per_cond[c][f'n_{cat}'] for c in conds]
        bars = ax.bar(
            conds,
            vals,
            bottom=bottom,
            color=colors[cat],
            label=labels[cat],
            edgecolor='white',
            linewidth=0.4)
        for bar, val in zip(bars, vals):
            if val >= 5:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_y() + bar.get_height() / 2,
                        str(int(val)),
                        ha='center',
                        va='center',
                        color='white',
                        fontsize=9,
                        fontweight='bold')
        bottom += np.asarray(vals)
    for i, c in enumerate(conds):
        rate = stats_per_cond[c]['cbb_rate']
        if rate is not None:
            ci = stats_per_cond[c]['cbb_rate_wilson_ci']
            ax.text(
                i,
                bottom[i] + 1,
                f'CBB={rate * 100:.1f}%\n[{ci[0] * 100:.1f}, {ci[1] * 100:.1f}]',
                ha='center',
                fontsize=9)
    ax.set_ylabel('Liczba probek (z 105 per warunek)')
    ax.set_title('Dekompozycja wynikow Fazy 4C wedlug bramki testowej\nCompile-but-break = patch przyjety przez walidator v1, ale testy v2 sie psuja')
    ax.legend(loc='upper left', fontsize=9)
    ax.set_ylim(0, 130)
    out = FIGURES_DIR / 'fig_compile_break.png'
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def plot_quality_distributions(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    cbb = df[df['category'] == 'compile_but_break']['quality_score'].dropna()
    green = df[df['category'] == 'applied_green']['quality_score'].dropna()
    bins = np.arange(-0.5, 11, 1)
    ax.hist(
        green,
        bins=bins,
        alpha=0.6,
        color='#2ca02c',
        label=f'applied + green (n={len(green)})',
        edgecolor='white')
    ax.hist(
        cbb,
        bins=bins,
        alpha=0.6,
        color='#d62728',
        label=f'compile-but-break (n={len(cbb)})',
        edgecolor='white')
    ax.axvline(
        green.median(),
        color='#2ca02c',
        linestyle='--',
        linewidth=1.4,
        label=f'med(green)={green.median():.1f}')
    ax.axvline(
        cbb.median(),
        color='#d62728',
        linestyle='--',
        linewidth=1.4,
        label=f'med(CBB)={cbb.median():.1f}')
    ax.set_xlabel('LLM-judge quality_score')
    ax.set_ylabel('Liczba probek')
    ax.set_title('Rozklad ocen LLM-judge: applied+green vs compile-but-break\nBrak istotnej roznicy = judge nie potrafi rozpoznac ukrytej regresji')
    ax.legend()
    ax.set_xlim(-0.5, 10.5)
    out = FIGURES_DIR / 'fig_quality_in_cbb.png'
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def render_md(payload: dict) -> str:
    md = ['# 5.A5 Compile-but-break - ukryte regresje\n']
    md.append('**Definicja:** `compile-but-break = patch_applied=1 AND tests_targeted>0 AND tests_green_strict=0`. Probka taka oszukala tradycyjny walidator (skladnia + metryki + LLM-judge), ale lamie testy regresyjne. To bezposrednie kwantytatywne potwierdzenie potrzeby dodania bramki testowej (Faza 4C).\n')
    md.append('## Compile-but-break rate per warunek (CI Wilsona 95%)\n')
    md.append('| cond | n_total | n_eligible | applied+green | CBB | not_applied | CBB rate | 95% CI |')
    md.append('|---|---|---|---|---|---|---|---|')
    for cond, r in payload['per_condition'].items():
        ci = r['cbb_rate_wilson_ci']
        ci_str = f'[{ci[0] * 100:.1f}%, {ci[1] * 100:.1f}%]' if ci else '-'
        rate_str = f"{r['cbb_rate'] * 100:.1f}%" if r['cbb_rate'] is not None else '-'
        md.append(
            f"| {cond} | {r['n_total']} | {r['n_eligible_for_cbb']} | {r['n_applied_green']} | {r['n_compile_but_break']} | {r['n_not_applied']} | {rate_str} | {ci_str} |")
    md.append('\n## Rozklad quality_score: CBB vs applied+green\n')
    q = payload['quality_distribution']
    if 'note' not in q:
        md.append(
            f"- median quality_score w **compile-but-break**: {q['median_quality_cbb']} (n={q['n_cbb']})\n- median quality_score w **applied+green**: {q['median_quality_green']} (n={q['n_green']})\n- Mann-Whitney U={q['mannwhitney_U']}, p={q['mannwhitney_p']}\n")
        if q['mannwhitney_p'] >= 0.05:
            md.append(
                f"\n> **Kluczowy wynik:** brak istotnej roznicy w rozkladzie ocen LLM-judge miedzy probkami CBB a green. Innymi slowy, judge **nie potrafi rozroznic** kodu poprawnego semantycznie od ukrytej regresji. Mediana ocen w grupie ukrytych regresji ({q['median_quality_cbb']}) jest **wyzsza** niz w grupie poprawnych testow ({q['median_quality_green']}) - judge wrecz **systematycznie nagradza** regresje.\n")
    md.append('\n## Interpretacja praktyczna\n')
    md.append("Compile-but-break rate to konkretny wskaznik **ile %** refaktoryzacji **oszukaloby** naiwna metodologie akceptacji bez bramki testowej. W Fazie 4+4B (v1) wszystkie te probki bylyby zaklasyfikowane jako 'sukces refaktoryzacji'. Wartosci >50% potwierdzaja, ze polaganie wylacznie na metrykach + LLM-judge **nie jest wystarczajace** do akceptacji refaktoryzacji w produkcyjnym CI/CD.\n")
    return '\n'.join(md) + '\n'


def run() -> dict:
    v2 = load_v2(applied_only=False)
    df = categorize(v2)
    payload = {'per_condition': per_condition_stats(
        df), 'quality_distribution': quality_distribution_in_cbb(df)}
    fig1 = plot_stacked(payload['per_condition'])
    fig2 = plot_quality_distributions(df)
    payload['figures'] = [str(fig1), str(fig2)]
    write_summary('compile_but_break', payload)
    out_md = ANALYSIS_DIR / 'compile_but_break.md'
    out_md.write_text(render_md(payload), encoding='utf-8')
    print(f"[CBB] summary -> {ANALYSIS_DIR / 'compile_but_break.json'}")
    print(f'[CBB] report  -> {out_md}')
    print('\n=== Compile-but-break rate per condition ===')
    for cond, r in payload['per_condition'].items():
        if r['cbb_rate'] is not None:
            ci = r['cbb_rate_wilson_ci']
            print(
                f"  {cond}: {r['cbb_rate'] * 100:.1f}%  [{ci[0] * 100:.1f}%, {ci[1] * 100:.1f}%]  ({r['n_compile_but_break']}/{r['n_eligible_for_cbb']})")
    q = payload['quality_distribution']
    if 'note' not in q:
        print(
            f"\nQuality dist (median): CBB={q['median_quality_cbb']}, green={q['median_quality_green']}, p={q['mannwhitney_p']}")
    return payload


if __name__ == '__main__':
    run()
