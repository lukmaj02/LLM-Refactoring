from __future__ import annotations
from scripts.analysis._dataio import ANALYSIS_DIR, load_v2
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
OUT = ANALYSIS_DIR / 'thesis_numbers.md'
LLM = ['A', 'G', 'C']
ALL = ['T', 'A', 'G', 'C']


def wilson(k: int, n: int) -> tuple[float, float]:
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method='wilson')
    return (100 * lo, 100 * hi)


def med_iqr(s: pd.Series) -> str:
    s = s.dropna()
    if s.empty:
        return '---'
    q1, q3 = (s.quantile(0.25), s.quantile(0.75))
    return f'{s.median():.2f} (IQR {q3 - q1:.2f})'


def gate_of(reason: str | None, accepted: int) -> str:
    if accepted == 1:
        return 'ACCEPT'
    if reason is None:
        return 'UNKNOWN'
    if reason.startswith('syntax_error'):
        return 'B1_syntax'
    if reason.startswith('empty_patch'):
        return 'B2_empty'
    if reason.startswith('no_metric'):
        return 'B3_metrics'
    if reason.startswith('test_failure'):
        return 'B4_tests'
    return f'OTHER:{reason}'


def main() -> None:
    df = load_v2()
    df['d_cc'] = df['cc_after'] - df['cc_before']
    df['d_mi'] = df['mi_after'] - df['mi_before']
    df['gate'] = [gate_of(r, a) for r, a in zip(df['rejection_reason'], df['patch_accepted'])]
    df['cc_tier'] = pd.cut(
        df['cc_before'], [
            0, 6, 9, np.inf], labels=[
            'CC 5-6', 'CC 7-9', 'CC >=10'])
    lines: list[str] = []
    w = lines.append
    w('# Liczby rozdziału 4 — jedyne źródło prawdy (faza 4C)')
    w('')
    w(f'Wygenerowano skryptem `scripts/analysis/thesis_numbers.py`; n = {len(df)} obserwacji.')
    w('')
    w('## 1. Przepływ przez bramki (tab:wyniki-kaskada)')
    w('')
    w('| Pozycja | T | A | G | C |')
    w('|---|---|---|---|---|')
    counts = {c: df[df.condition == c] for c in ALL}
    row_n = {c: len(counts[c]) for c in ALL}
    b1 = {c: (counts[c].gate != 'B1_syntax').sum() for c in ALL}
    b2 = {c: b1[c] - (counts[c].gate == 'B2_empty').sum() for c in ALL}
    b3 = {c: b2[c] - (counts[c].gate == 'B3_metrics').sum() for c in ALL}
    b4 = {c: (counts[c].gate == 'ACCEPT').sum() for c in ALL}
    for label, d in [('Wejście', row_n), ('po B1 (składnia)', b1), ('po B2 (niepusta zmiana)',
                                                                    b2), ('po B3 (metryki)', b3), ('po B4 (testy) = akceptacja', b4)]:
        w(f'| {label} | ' + ' | '.join((str(d[c]) for c in ALL)) + ' |')
    w('')
    w('Odsetek akceptacji (z 95% CI Wilsona):')
    w('')
    for c in ALL:
        k, n = (b4[c], row_n[c])
        lo, hi = wilson(k, n)
        w(f'* {c}: {k}/{n} = {100 * k / n:.1f}% (CI {lo:.1f}–{hi:.1f})')
    k_llm = sum((b4[c] for c in LLM))
    n_llm = sum((row_n[c] for c in LLM))
    lo, hi = wilson(k_llm, n_llm)
    w(f'* A+G+C łącznie: {k_llm}/{n_llm} = {100 * k_llm / n_llm:.2f}% (CI {lo:.1f}–{hi:.1f})')
    w('')
    w('## 2. Compile-but-break (tab:wyniki-cbb)')
    w('')
    w('CBB = test_failure / (obserwacje, które przeszły B1–B3).')
    w('')
    for c in ALL:
        denom = b3[c]
        k = (counts[c].gate == 'B4_tests').sum()
        if denom:
            lo, hi = wilson(k, denom)
            w(f'* {c}: {k}/{denom} = {100 * k / denom:.1f}% (CI {lo:.1f}–{hi:.1f})')
    w('')
    w('### CBB wg repozytorium (tylko A/G/C)')
    w('')
    llm = df[df.condition.isin(LLM)]
    for repo, g in llm.groupby('repo'):
        denom = ((g.gate == 'B4_tests') | (g.gate == 'ACCEPT')).sum()
        k = (g.gate == 'B4_tests').sum()
        lo, hi = wilson(k, denom)
        w(f'* {repo}: {k}/{denom} = {100 * k / denom:.1f}% (CI {lo:.1f}–{hi:.1f})')
    tab = pd.crosstab(llm[llm.gate.isin(['B4_tests', 'ACCEPT'])].repo,
                      llm[llm.gate.isin(['B4_tests', 'ACCEPT'])].gate)
    if tab.shape == (3, 2):
        _, p = stats.fisher_exact(tab.iloc[:2, :]) if False else (None, None)
        chi2, p_chi, *_ = stats.chi2_contingency(tab)
        w(f'* test niezależności repo×CBB: chi2 = {chi2:.2f}, p = {p_chi:.3f}')
    w('')
    w('### CBB wg warstwy CC (tylko A/G/C)')
    w('')
    sub = llm[llm.gate.isin(['B4_tests', 'ACCEPT'])]
    for tier, g in sub.groupby('cc_tier', observed=True):
        k, denom = ((g.gate == 'B4_tests').sum(), len(g))
        lo, hi = wilson(k, denom)
        w(f'* {tier}: {k}/{denom} = {100 * k / denom:.1f}% (CI {lo:.1f}–{hi:.1f})')
    tab = pd.crosstab(sub.cc_tier, sub.gate)
    chi2, p_chi, *_ = stats.chi2_contingency(tab)
    w(f'* test niezależności warstwa×CBB: chi2 = {chi2:.2f}, p = {p_chi:.3f}')
    w('')
    w('## 3. Kryterium surowe vs złagodzone (sygnał linii bazowej testów)')
    w('')
    w('`green_relaxed` dopuszcza dokładnie 1 oblany test (podejrzenie testu')
    w('failującego bazowo w środowisku — do weryfikacji w Etapie 1.3).')
    w('')
    w('| Warunek | akceptacja strict | akceptacja relaxed (failed<=1) |')
    w('|---|---|---|')
    for c in ALL:
        g = counts[c]
        reach_b4 = g[g.gate.isin(['B4_tests', 'ACCEPT'])]
        strict = (reach_b4.tests_green_strict == 1).sum()
        relax = (reach_b4.tests_green_relaxed == 1).sum()
        w(f'| {c} | {strict}/{len(reach_b4)} | {relax}/{len(reach_b4)} |')
    w('')
    only1 = df[(df.gate == 'B4_tests') & (df.tests_failed == 1) & (df.tests_errors.fillna(0) == 0)]
    w(f"Obserwacje odrzucone przez B4 z DOKŁADNIE 1 oblanym testem: {len(only1)} z {(df.gate == 'B4_tests').sum()} wszystkich test_failure.")
    w('')
    w('## 4. Statystyki opisowe (tab:wyniki-eda-deskryptywka)')
    w('')
    w('| Zmienna | T | A | G | C |')
    w('|---|---|---|---|---|')
    for var, label in [('d_cc', 'ΔCC (po-przed)'), ('d_mi', 'ΔMI'), ('pass_ratio', 'pass_ratio'),
                       ('quality_score', 'quality_score'), ('semantic_score', 'semantic_score')]:
        cells = [med_iqr(counts[c][var]) for c in ALL]
        w(f'| {label} | ' + ' | '.join(cells) + ' |')
    w('')
    dcc = llm['d_cc'].dropna()
    w(f'ΔCC (A+G+C, n={len(dcc)}): średnia = {dcc.mean():.2f}, mediana = {dcc.median():.1f}, SD = {dcc.std():.2f}')
    boot = [np.random.default_rng(7 + i).choice(dcc, len(dcc)).mean() for i in range(2000)]
    w(f'95% CI (bootstrap, percentyle) średniej ΔCC: [{np.percentile(boot, 2.5):.2f}; {np.percentile(boot, 97.5):.2f}]')
    w('')
    w('## 5. Normalność (Shapiro–Wilk)')
    w('')
    for var in ['d_cc', 'd_mi', 'pass_ratio', 'quality_score']:
        s = llm[var].dropna()
        if len(s) > 3:
            W, p = stats.shapiro(s.sample(min(len(s), 4999), random_state=1))
            w(f'* {var}: W = {W:.3f}, p = {p:.2e}, n = {len(s)}')
    w('')
    w('## 6. PB1: Wilcoxon (H: ΔCC < 0)')
    w('')
    for c in LLM + [None]:
        s = (llm if c is None else counts[c])['d_cc'].dropna()
        s = s[s != 0]
        res = stats.wilcoxon(s, alternative='less', method='approx')
        z = getattr(res, 'zstatistic', np.nan)
        r = z / np.sqrt(len(s)) if len(s) else np.nan
        name = c or 'A+G+C'
        w(f'* {name}: W = {res.statistic:.0f}, z = {z:.2f}, p = {res.pvalue:.2e}, r = {r:.2f}, n = {len(s)}')
    w('')
    w('## 7. PB2: porównanie modeli')
    w('')
    groups = [counts[c]['d_cc'].dropna() for c in LLM]
    H, p = stats.kruskal(*groups)
    n_tot = sum((len(g) for g in groups))
    eps2 = (H - 3 + 1) / (n_tot - 3)
    w(f'* Kruskal–Wallis (ΔCC, grupy A/G/C): H = {H:.2f}, p = {p:.3f}, epsilon^2 = {eps2:.3f}, n = {n_tot}')
    piv = llm.pivot_table(index='sample_id', columns='condition', values='d_cc')
    complete = piv.dropna()
    fr = stats.friedmanchisquare(complete['A'], complete['G'], complete['C'])
    w(f'* Friedman (ΔCC, pary kompletne): chi2 = {fr.statistic:.2f}, p = {fr.pvalue:.3f}, n = {len(complete)}')
    w('* Parowane Wilcoxony (ΔCC):')
    pvals = []
    for a, b in [('A', 'G'), ('A', 'C'), ('G', 'C')]:
        pair = piv[[a, b]].dropna()
        diff = pair[a] - pair[b]
        diff = diff[diff != 0]
        res = stats.wilcoxon(diff, method='approx')
        pvals.append((f'{a} vs {b}', res.pvalue, len(diff)))
    from statsmodels.stats.multitest import multipletests
    rej, p_adj, *_ = multipletests([p for _, p, _ in pvals], method='fdr_bh')
    for (name, p_raw, n), pa in zip(pvals, p_adj):
        w(f'  * {name}: p = {p_raw:.3f}, p_FDR = {pa:.3f}, n = {n}')
    acc_piv = llm.pivot_table(
        index='sample_id',
        columns='condition',
        values='patch_accepted').dropna()
    from statsmodels.stats.contingency_tables import cochrans_q
    q = cochrans_q(acc_piv[['A', 'G', 'C']].values)
    w(f'* Cochran Q (akceptacja, pary): Q = {q.statistic:.2f}, p = {q.pvalue:.3f}, n = {len(acc_piv)}')
    tab = pd.DataFrame({c: [b4[c], row_n[c] - b4[c]] for c in LLM}).T
    chi2, p_f, *_ = stats.chi2_contingency(tab)
    w(f'* chi2 niezależności akceptacja×model (odpowiednik Fishera): chi2 = {chi2:.2f}, p = {p_f:.3f}')
    w('')
    w('## 8. PB3: sędzia vs testy')
    w('')
    sub = llm.dropna(subset=['quality_score', 'pass_ratio'])
    rho, p_rho = stats.spearmanr(sub.quality_score, sub.pass_ratio)
    r_p, p_p = stats.pearsonr(sub.quality_score, sub.pass_ratio)
    w(f'* Spearman rho = {rho:.3f}, p = {p_rho:.3f}, n = {len(sub)} (A/G/C)')
    w(f'* Pearson r = {r_p:.3f}, p = {p_p:.3f} (dla porównania)')
    sub_t = df.dropna(subset=['quality_score', 'pass_ratio'])
    rho_t, p_t = stats.spearmanr(sub_t.quality_score, sub_t.pass_ratio)
    w(f'* Spearman z warunkiem T: rho = {rho_t:.3f}, p = {p_t:.3f}, n = {len(sub_t)}')
    w('')
    w('## 9. PB4: regresja logistyczna (tests_green_strict)')
    w('')
    import statsmodels.formula.api as smf
    mdl_df = llm.dropna(
        subset=[
            'quality_score',
            'd_cc',
            'changed_pct',
            'tests_green_strict']).copy()
    try:
        m = smf.logit(
            'tests_green_strict ~ quality_score + d_cc + changed_pct + C(condition)',
            data=mdl_df).fit(
            disp=False)
        w('| Predyktor | OR | 95% CI | p |')
        w('|---|---|---|---|')
        ci = m.conf_int()
        for name in m.params.index:
            if name == 'Intercept':
                continue
            orr = np.exp(m.params[name])
            lo_, hi_ = np.exp(ci.loc[name])
            w(f'| {name} | {orr:.3f} | [{lo_:.3f}; {hi_:.3f}] | {m.pvalues[name]:.3f} |')
        pred = m.predict(mdl_df)
        y = mdl_df['tests_green_strict'].values
        n1, n0 = ((y == 1).sum(), (y == 0).sum())
        ranks = stats.rankdata(pred)
        auc = (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
        w('')
        w(f'AUC = {auc:.3f} (0,5 = klasyfikator losowy); n = {len(mdl_df)}, zdarzenia = {n1}')
    except Exception as e:
        w(f'Uwaga: model nie zbiega ({e}); raportować modele jednoczynnikowe.')
    w('')
    w('## 10. Koszty i czasy (Etap 1.6)')
    w('')
    w('| Warunek | mediana tokens_out | mediana czasu [s] | suma kosztu [USD] |')
    w('|---|---|---|---|')
    for c in LLM:
        g = counts[c]
        w(f'| {c} | {g.tokens_out.median():.0f} | {g.response_time_s.median():.1f} | {g.cost_usd.sum():.2f} |')
    w('')
    w('## 11. Zgodność między modelami (CBB na tych samych migawkach)')
    w('')
    cbb_piv = llm.assign(cbb=(llm.gate == 'B4_tests').astype(int)).pivot_table(
        index='sample_id', columns='condition', values='cbb').dropna()
    for a, b in [('A', 'G'), ('A', 'C'), ('G', 'C')]:
        inter = ((cbb_piv[a] == 1) & (cbb_piv[b] == 1)).sum()
        union = ((cbb_piv[a] == 1) | (cbb_piv[b] == 1)).sum()
        w(f'* Jaccard CBB {a}∩{b}: {inter}/{union} = {inter / union:.2f}')
    all3 = (cbb_piv == 1).all(axis=1).sum()
    w(f'* migawki z CBB we wszystkich trzech modelach: {all3}/{len(cbb_piv)}')
    w('')
    w('## 12. CBB skorygowane o linię bazową (Etap 1.3a)')
    w('')
    w('Warunek T (sam autopep8/autoflake) nie zmienia zachowania programu, więc')
    w('jego wynik testów na danej migawce traktujemy jako linię bazową środowiska.')
    w('Regresja przypisywalna refaktoryzacji = model obla WIĘCEJ testów niż T')
    w('na tej samej migawce (failures+errors).')
    w('')
    df['fail_all'] = df['tests_failed'].fillna(0) + df['tests_errors'].fillna(0)
    reach = df[df.gate.isin(['B4_tests', 'ACCEPT'])]
    base = reach[reach.condition == 'T'].set_index('sample_id')['fail_all']
    w('| Warunek | n par z T | regresja > baseline | CBB skorygowane | CI Wilsona |')
    w('|---|---|---|---|---|')
    corr_flags = {}
    for c in LLM:
        g = reach[reach.condition == c].set_index('sample_id')
        common = g.index.intersection(base.index)
        gx = g.loc[common]
        worse = (gx['fail_all'] > base.loc[common]).astype(int)
        corr_flags[c] = worse
        k, n = (int(worse.sum()), len(worse))
        lo, hi = wilson(k, n)
        w(f'| {c} | {n} | {k} | {100 * k / n:.1f}% | [{lo:.1f}; {hi:.1f}] |')
    w('')
    sel = df.pivot_table(
        index='sample_id',
        columns='condition',
        values='tests_run',
        aggfunc='first')
    mism = {c: int((sel[c].dropna() != sel['T'].reindex(sel[c].dropna().index)).sum())
            for c in LLM if c in sel}
    w(f'Kontrola spójności doboru testów (liczba plików testowych rożna niż w T): {mism}')
    w('')
    w('Akceptacja skorygowana (przeszło B1–B3 i nie obla więcej testów niż T,')
    w('w mianowniku pełne n=105 na warunek):')
    w('')
    for c in LLM:
        worse = corr_flags[c]
        k = int((worse == 0).sum())
        lo, hi = wilson(k, 105)
        w(f'* {c}: {k}/105 = {100 * k / 105:.1f}% (CI {lo:.1f}–{hi:.1f})')
    w('')
    w('Uwaga interpretacyjna: korekta zakłada, że T i model dostały ten sam')
    w('zestaw testów (kontrola powyżej) oraz że zmiany T są semantycznie')
    w('neutralne (autopep8 formatuje; autoflake usuwa nieużywane importy —')
    w('ryzyko naruszenia importów z efektem ubocznym omówić w ograniczeniach).')
    w('')
    w('## 13. Zaakceptowane refaktoryzacje (Etap 1.4)')
    w('')
    acc = df[df.gate == 'ACCEPT'].sort_values(['condition', 'sample_id'])
    w('| sample_id | warunek | repo | CC przed→po | MI przed→po | quality |')
    w('|---|---|---|---|---|---|')
    for _, r in acc.iterrows():
        w(f'| {r.sample_id} | {r.condition} | {r.repo} | {r.cc_before:.0f}→{r.cc_after:.0f} | {r.mi_before:.1f}→{r.mi_after:.1f} | {r.quality_score} |')
    w('')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'OK -> {OUT}')


if __name__ == '__main__':
    main()
