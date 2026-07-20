from __future__ import annotations
from scripts.analysis._dataio import _connect, load_v2
from scipy import stats
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'thesis_v2_promotor' / 'figures' / 'results'
ALL = ['T', 'A', 'G', 'C']
LLM = ['A', 'G', 'C']
LABELS = {'T': 'T (autopep8)', 'A': 'A (GPT-4o)', 'G': 'G (Gemini)', 'C': 'C (Claude)'}
COLORS = {'T': '#9e9e9e', 'A': '#1f77b4', 'G': '#2ca02c', 'C': '#d62728'}
plt.rcParams.update({'font.size': 10,
                     'axes.spines.top': False,
                     'axes.spines.right': False,
                     'figure.dpi': 150,
                     'savefig.bbox': 'tight'})


def wilson(k, n):
    from statsmodels.stats.proportion import proportion_confint
    return proportion_confint(k, n, alpha=0.05, method='wilson')


def gate_of(reason, accepted):
    if accepted == 1:
        return 'akceptacja'
    if reason is None:
        return 'inne'
    if reason.startswith('syntax_error'):
        return 'błąd składni (B1)'
    if reason.startswith('no_metric'):
        return 'brak poprawy metryk (B3)'
    if reason.startswith('test_failure'):
        return 'testy nie przechodzą (B4)'
    return 'inne'


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name)
    plt.close(fig)
    print('  ->', name)


def main() -> None:
    df = load_v2()
    df['d_cc'] = df['cc_after'] - df['cc_before']
    df['d_mi'] = df['mi_after'] - df['mi_before']
    df['gate'] = [gate_of(r, a) for r, a in zip(df['rejection_reason'], df['patch_accepted'])]
    df['fail_all'] = df['tests_failed'].fillna(0) + df['tests_errors'].fillna(0)
    cats = [
        'akceptacja',
        'testy nie przechodzą (B4)',
        'brak poprawy metryk (B3)',
        'błąd składni (B1)']
    cat_colors = ['#2e7d32', '#c62828', '#f9a825', '#6a1b9a']
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    bottoms = np.zeros(len(ALL))
    for cat, col in zip(cats, cat_colors):
        vals = [len(df[(df.condition == c) & (df.gate == cat)]) for c in ALL]
        ax.bar([LABELS[c] for c in ALL], vals, bottom=bottoms, label=cat, color=col)
        bottoms += np.array(vals)
    ax.set_ylabel('Liczba obserwacji (na 105)')
    ax.legend(frameon=False, fontsize=8, ncol=2, loc='lower center', bbox_to_anchor=(0.5, 1.0))
    save(fig, 'fig4_kaskada_przeplyw.pdf')
    fig, ax = plt.subplots(figsize=(6.0, 3.2))
    data = [df[df.condition == c]['d_cc'].dropna() for c in ALL]
    bp = ax.boxplot(
        data,
        tick_labels=[
            LABELS[c] for c in ALL],
        patch_artist=True,
        medianprops=dict(
            color='black'))
    for patch, c in zip(bp['boxes'], ALL):
        patch.set_facecolor(COLORS[c])
        patch.set_alpha(0.55)
    ax.axhline(0, ls=':', c='gray', lw=0.8)
    ax.set_ylabel('$\\Delta$CC (po $-$ przed)')
    save(fig, 'fig4_delta_cc_box.pdf')
    llm = df[df.condition.isin(LLM)]
    for var, xlab, name in [('d_cc', '$\\Delta$CC (po $-$ przed)', 'fig4_hist_dcc.pdf'),
                            ('d_mi', '$\\Delta$MI (po $-$ przed)', 'fig4_hist_dmi.pdf')]:
        fig, ax = plt.subplots(figsize=(3.6, 2.8))
        ax.hist(llm[var].dropna(), bins=30, color='#1d3557', alpha=0.85)
        ax.set_xlabel(xlab)
        ax.set_ylabel('Liczba obserwacji')
        save(fig, name)
    fig, ax = plt.subplots(figsize=(3.6, 2.8))
    stats.probplot(llm['d_cc'].dropna(), dist='norm', plot=ax)
    ax.set_title('')
    ax.get_lines()[0].set(color='#1d3557', markersize=3)
    ax.set_xlabel('Kwantyle teoretyczne (rozkład normalny)')
    ax.set_ylabel('Kwantyle $\\Delta$CC')
    save(fig, 'fig4_qq_dcc.pdf')
    with _connect() as con:
        vd = pd.read_sql_query('SELECT sample_id, condition, verdict FROM regression_verdicts', con)
        rr = pd.read_sql_query(
            "SELECT sample_id, condition, patch_ok FROM test_gate_rerun WHERE condition != 'BASE'", con)
    verdicts = {(r.sample_id, r.condition): r.verdict for r in vd.itertuples()}
    struct_ok = {}
    for r in df.itertuples():
        ok = r.rejection_reason is None or str(r.rejection_reason).startswith('test_failure')
        struct_ok[r.sample_id, r.condition] = ok
    acc_k, reg_k = ({}, {})
    for c in ALL:
        acc = 0
        for r in rr[rr.condition == c].itertuples():
            if r.patch_ok == 0 or not struct_ok.get((r.sample_id, c), False):
                continue
            if verdicts.get((r.sample_id, c)) == 'confirmed':
                continue
            acc += 1
        acc_k[c] = acc
        reg_k[c] = int(vd[(vd.condition == c) & (vd.verdict == 'confirmed')].shape[0])
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    x = np.arange(len(ALL))
    w = 0.38
    for off, (label, kdict, col) in enumerate([('akceptacja końcowa (brak potwierdzonej regresji)',
                                                acc_k, '#2e7d32'), ('potwierdzone regresje względem linii bazowej', reg_k, '#c62828')]):
        ks = [kdict[c] for c in ALL]
        props = [k / 105 for k in ks]
        cis = [wilson(k, 105) for k in ks]
        err = np.array([[p - lo, hi - p] for p, (lo, hi) in zip(props, cis)]).T
        ax.bar(x + (off - 0.5) * w, props, w, yerr=err,
               capsize=3, label=label, color=col, alpha=0.85)
    ax.set_xticks(x, [LABELS[c] for c in ALL])
    ax.set_ylabel('Odsetek obserwacji (n = 105)')
    ax.set_ylim(0, 1.1)
    ax.legend(frameon=False, fontsize=8, loc='lower center', bbox_to_anchor=(0.5, 1.0), ncol=1)
    save(fig, 'fig4_akceptacja.pdf')
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    rng = np.random.default_rng(1)
    for c in LLM:
        g = llm[llm.condition == c].dropna(subset=['quality_score', 'pass_ratio'])
        ax.scatter(g.quality_score + rng.uniform(-0.15, 0.15, len(g)),
                   g.pass_ratio, s=14, alpha=0.5, color=COLORS[c], label=LABELS[c])
    ax.set_xlabel('Ocena ogólna sędziego (quality, 0–10)')
    ax.set_ylabel('Odsetek testów przechodzących')
    ax.legend(frameon=False, fontsize=8, loc='lower left')
    save(fig, 'fig4_judge_vs_tests.pdf')
    with _connect() as con:
        r2 = pd.read_sql_query('SELECT * FROM judge_retest', con)
    r1 = df[['sample_id', 'condition', 'solid_score', 'dry_score',
             'kiss_score', 'semantic_score', 'quality_score']]
    m = r1.merge(r2, on=['sample_id', 'condition'], suffixes=('_1', '_2'))
    from scripts.analysis.judge_retest_analysis import icc21, icc_ci
    dims = ['solid_score', 'quality_score', 'kiss_score', 'semantic_score', 'dry_score']
    dim_pl = {
        'solid_score': 'SOLID',
        'dry_score': 'DRY',
        'kiss_score': 'KISS',
        'semantic_score': 'semantyka',
        'quality_score': 'jakość ogólna'}
    fig, ax = plt.subplots(figsize=(5.6, 3.0))
    ys = np.arange(len(dims))
    for y, d in zip(ys, dims):
        a = m[f'{d}_1'].to_numpy(float)
        b = m[f'{d}_2'].to_numpy(float)
        icc = icc21(a, b)
        lo, hi = icc_ci(a, b, n_boot=2000)
        ax.errorbar(icc, y, xerr=[[icc - lo], [hi - icc]], fmt='o', color='#1d3557', capsize=3)
        ax.text(hi + 0.02, y, f'{icc:.2f}', va='center', fontsize=8)
    ax.axvline(0.5, ls=':', c='gray', lw=0.8)
    ax.axvline(0.75, ls=':', c='gray', lw=0.8)
    ax.set_yticks(ys, [dim_pl[d] for d in dims])
    ax.set_xlabel('ICC(2,1) z 95% CI (bootstrap)')
    ax.set_xlim(0, 1.05)
    save(fig, 'fig4_retest_icc.pdf')
    d = m['quality_score_2'] - m['quality_score_1']
    avg = (m['quality_score_2'] + m['quality_score_1']) / 2
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    ax.scatter(avg + rng.uniform(-0.1, 0.1, len(avg)), d, s=14, alpha=0.5, color='#1d3557')
    mean_d, sd = (d.mean(), d.std(ddof=1))
    for yv, ls in [(mean_d, '-'), (mean_d - 1.96 * sd, '--'), (mean_d + 1.96 * sd, '--')]:
        ax.axhline(yv, ls=ls, c='#c62828', lw=1)
    ax.set_xlabel('Średnia z dwóch ocen (quality, 0–10)')
    ax.set_ylabel('Różnica ocen (retest $-$ test)')
    save(fig, 'fig4_bland_altman.pdf')
    import statsmodels.formula.api as smf
    mdl = llm.merge(vd, on=['sample_id', 'condition'], how='left')
    mdl['confirmed'] = (mdl.verdict == 'confirmed').astype(int)
    mdl = mdl.dropna(subset=['d_cc', 'changed_pct']).copy()
    fit = smf.logit('confirmed ~ d_cc + changed_pct + C(condition)', data=mdl).fit(disp=False)
    names = [n for n in fit.params.index if n != 'Intercept']
    pl = {
        'quality_score': 'ocena sędziego (quality)',
        'd_cc': '$\\Delta$CC',
        'changed_pct': 'odsetek zmienionych linii',
        'C(condition)[T.G]': 'model G (vs A)',
        'C(condition)[T.C]': 'model C (vs A)'}
    fig, ax = plt.subplots(figsize=(5.8, 3.0))
    ci = fit.conf_int()
    for y, nme in enumerate(names):
        orr = np.exp(fit.params[nme])
        lo, hi = np.exp(ci.loc[nme])
        ax.errorbar(orr, y, xerr=[[orr - lo], [hi - orr]], fmt='s', color='#1d3557', capsize=3)
    ax.axvline(1, ls=':', c='gray')
    ax.set_yticks(range(len(names)), [pl.get(n, n) for n in names])
    ax.set_xscale('log')
    ax.set_xlabel('Iloraz szans (OR, skala log.) z 95% CI')
    save(fig, 'fig4_logit_or.pdf')
    print('OK — wykresy w', OUT)


if __name__ == '__main__':
    main()
