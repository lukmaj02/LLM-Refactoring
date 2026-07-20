from __future__ import annotations
from _dataio import ANALYSIS_DIR, DB_PATH, load_v1, load_v2, paired_table_v2, write_summary
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sqlite3
import scikit_posthocs as sph
from scipy import stats
from statsmodels.stats.multitest import multipletests
sys.path.insert(0, str(Path(__file__).resolve().parent))
ALPHA = 0.05


def _wilcoxon_one_sample(values, mu0=0, *, alternative='two-sided'):
    arr = np.asarray([v for v in values if v is not None and (not np.isnan(v))])
    if len(arr) < 5:
        return {'n': int(len(arr)), 'stat': None, 'p': None, 'alternative': alternative}
    try:
        res = stats.wilcoxon(
            arr - mu0,
            alternative=alternative,
            zero_method='wilcox',
            method='auto')
    except ValueError:
        return {'n': int(len(arr)), 'stat': None, 'p': None,
                'alternative': alternative, 'note': 'no non-zero differences'}
    return {'n': int(len(arr)), 'median': float(np.median(arr)), 'stat': round(
        float(res.statistic), 3), 'p': round(float(res.pvalue), 6), 'alternative': alternative}


def _wilcoxon_paired(a, b):
    pairs = [
        (x, y) for x, y in zip(
            a, b) if x is not None and y is not None and (
            not (
                np.isnan(x) or np.isnan(y)))]
    if len(pairs) < 5:
        return {'n_pairs': int(len(pairs)), 'stat': None, 'p': None}
    x, y = zip(*pairs)
    try:
        res = stats.wilcoxon(
            np.asarray(x),
            np.asarray(y),
            alternative='two-sided',
            zero_method='wilcox')
    except ValueError:
        return {'n_pairs': int(len(pairs)), 'stat': None, 'p': None, 'note': 'all differences zero'}
    diffs = np.asarray(x) - np.asarray(y)
    return {'n_pairs': int(len(pairs)), 'median_diff': round(float(np.median(diffs)), 3), 'stat': round(float(
        res.statistic), 3), 'p': round(float(res.pvalue), 6), 'effect_r': round(_wilcoxon_r(res.statistic, len(pairs)), 3)}


def _wilcoxon_r(stat: float, n: int) -> float:
    mu = n * (n + 1) / 4.0
    sd = np.sqrt(n * (n + 1) * (2 * n + 1) / 24.0)
    if sd == 0:
        return 0.0
    z = (stat - mu) / sd
    return float(abs(z) / np.sqrt(n))


def _kruskal(*groups):
    cleaned = [np.asarray([v for v in g if v is not None and (not np.isnan(v))]) for g in groups]
    if min((len(g) for g in cleaned)) < 3:
        return {'k': len(groups), 'n_total': sum((len(g) for g in cleaned)), 'H': None, 'p': None}
    try:
        res = stats.kruskal(*cleaned)
    except ValueError:
        return {'k': len(groups), 'n_total': sum((len(g) for g in cleaned)), 'H': None, 'p': None}
    n = sum((len(g) for g in cleaned))
    k = len(cleaned)
    epsilon_sq = (res.statistic - k + 1) / (n - k) if n > k else None
    return {'k': k, 'n_total': int(n), 'H': round(float(res.statistic), 3), 'p': round(
        float(res.pvalue), 6), 'epsilon_sq': round(float(epsilon_sq), 4) if epsilon_sq is not None else None}


def _dunn_posthoc(df: pd.DataFrame, *, metric: str, group_col: str) -> dict:
    sub = df[[metric, group_col]].dropna()
    if sub.empty:
        return {'k_pairs': 0, 'pairs': [], 'method': 'dunn-bonferroni'}
    groups = sorted(sub[group_col].unique())
    pmat = sph.posthoc_dunn(sub, val_col=metric, group_col=group_col, p_adjust='bonferroni')
    pairs = []
    counts = sub.groupby(group_col).size().to_dict()
    for i in range(len(groups)):
        for j in range(i + 1, len(groups)):
            g_a, g_b = (groups[i], groups[j])
            try:
                p_adj = float(pmat.loc[g_a, g_b])
            except KeyError:
                continue
            pairs.append({'pair': f'{g_a} vs {g_b}', 'n_a': int(counts.get(g_a, 0)), 'n_b': int(
                counts.get(g_b, 0)), 'p_bonferroni': round(p_adj, 6), 'significant_005': bool(p_adj < ALPHA)})
    return {'k_pairs': len(pairs), 'pairs': pairs, 'method': 'dunn-bonferroni (scikit-posthocs)'}


def _fisher_2x2(table) -> dict:
    res = stats.fisher_exact(table)
    return {'table': [[int(x) for x in row] for row in table], 'odds_ratio': round(
        float(res.statistic), 3), 'p': round(float(res.pvalue), 6)}


def _spearman(x, y) -> dict:
    pairs = [
        (a, b) for a, b in zip(
            x, y) if a is not None and b is not None and (
            not (
                pd.isna(a) or pd.isna(b)))]
    if len(pairs) < 5:
        return {'n': int(len(pairs)), 'rho': None, 'p': None}
    xs, ys = zip(*pairs)
    res = stats.spearmanr(xs, ys)
    return {'n': int(len(pairs)), 'rho': round(float(res.statistic), 3),
            'p': round(float(res.pvalue), 6)}


def H1_semantic_equivalence(v2: pd.DataFrame, *, mu0: int = 8) -> dict:
    out = {
        'description': f"H0: median(semantic_score) >= {mu0} vs H1: median < {mu0} (Wilcoxon one-sample, alternative='less')",
        'results': {},
        'alpha': ALPHA,
        'mu0': mu0}
    for cond, sub in v2.groupby('condition'):
        out['results'][str(cond)] = _wilcoxon_one_sample(
            sub['semantic_score'].dropna().tolist(), mu0=mu0, alternative='less')
    return out


def H2_AI_vs_T(v2: pd.DataFrame) -> dict:
    pivot = paired_table_v2(v2, conditions=('T', 'A', 'G', 'C'))
    out = {'description': 'Paired Wilcoxon on delta_cc, AI vs T (same samples)', 'results': {
    }, 'alpha': ALPHA}
    for cond in ('A', 'G', 'C'):
        if cond in pivot.columns and 'T' in pivot.columns:
            out['results'][f'{cond}_vs_T'] = _wilcoxon_paired(
                pivot[cond].tolist(), pivot['T'].tolist())
    return out


def H3_AI_models(v2: pd.DataFrame) -> dict:
    sub = v2[v2['condition'].isin(['A', 'G', 'C'])].copy()
    sub = sub.dropna(subset=['delta_cc'])
    a = sub[sub['condition'] == 'A']['delta_cc'].tolist()
    g = sub[sub['condition'] == 'G']['delta_cc'].tolist()
    c = sub[sub['condition'] == 'C']['delta_cc'].tolist()
    out = {
        'description': 'Kruskal-Wallis: delta_cc across A, G, C',
        'kruskal': _kruskal(
            a,
            g,
            c),
        'dunn_posthoc': _dunn_posthoc(
            sub,
            metric='delta_cc',
            group_col='condition'),
        'alpha': ALPHA}
    return out


def H4_cicd_overhead() -> dict:
    with sqlite3.connect(str(DB_PATH)) as conn:
        df = pd.read_sql_query('SELECT * FROM pipeline_runs', conn)
    pivot = df.pivot_table(
        index=[
            'repo',
            'commit_hash'],
        columns='config',
        values='total_duration_s',
        aggfunc='first')
    baseline = pivot.get('baseline')
    arp = pivot.get('arp')
    if baseline is None or arp is None:
        return {'description': 'CI/CD overhead', 'error': 'missing config'}
    return {'description': 'Paired Wilcoxon: baseline vs arp pipeline duration', 'n_commits': int(len(pivot)), 'wilcoxon': _wilcoxon_paired(arp.tolist(), baseline.tolist(
    )), 'median_baseline_s': round(float(baseline.median()), 2), 'median_arp_s': round(float(arp.median()), 2), 'median_overhead_s': round(float((arp - baseline).median()), 2), 'alpha': ALPHA}


def H5_judge_vs_tests(v2: pd.DataFrame) -> dict:
    sub = v2[(v2['tests_targeted'].fillna(0) > 0) &
             v2['quality_score'].notna() & v2['pass_ratio'].notna()].copy()
    spearman_overall = _spearman(sub['quality_score'], sub['pass_ratio'])
    by_cond = {}
    for cond, group in sub.groupby('condition'):
        by_cond[str(cond)] = _spearman(group['quality_score'], group['pass_ratio'])
    green = sub[sub['tests_green_strict'] == 1]['quality_score']
    notgreen = sub[sub['tests_green_strict'] == 0]['quality_score']
    if len(green) >= 3 and len(notgreen) >= 3:
        u_res = stats.mannwhitneyu(green, notgreen, alternative='two-sided')
        mw = {
            'n_green': int(
                len(green)), 'n_notgreen': int(
                len(notgreen)), 'median_green': round(
                float(
                    green.median()), 2), 'median_notgreen': round(
                        float(
                            notgreen.median()), 2), 'U': round(
                                float(
                                    u_res.statistic), 3), 'p': round(
                                        float(
                                            u_res.pvalue), 6)}
    else:
        mw = {'n_green': int(len(green)), 'n_notgreen': int(len(notgreen)), 'p': None}
    return {'description': 'H5: czy LLM-judge koreluje z faktycznym pass rate testow?', 'spearman_overall': spearman_overall,
            'spearman_per_condition': by_cond, 'mann_whitney_green_vs_notgreen': mw, 'alpha': ALPHA}


def H6_accept_v1_vs_v2(v1: pd.DataFrame, v2: pd.DataFrame) -> dict:
    rows = {}
    for cond in ('A', 'G', 'C', 'T'):
        a1 = int(v1[(v1['condition'] == cond) & (v1['patch_accepted'] == 1)].shape[0])
        r1 = int(v1[(v1['condition'] == cond) & (v1['patch_accepted'] == 0)].shape[0])
        a2 = int(v2[(v2['condition'] == cond) & (v2['patch_accepted'] == 1)].shape[0])
        r2 = int(v2[(v2['condition'] == cond) & (v2['patch_accepted'] == 0)].shape[0])
        rows[cond] = _fisher_2x2([[a1, r1], [a2, r2]])
    return {
        'description': 'Roznica accept rate v1 (Faza 4+4B) vs v2 (Faza 4C) per warunek', 'results': rows, 'alpha': ALPHA}


def _collect_pvalues(payload: dict) -> list[tuple[str, float, dict]]:
    items: list[tuple[str, float, dict]] = []
    for cond, r in payload['H1']['results'].items():
        if r.get('p') is not None:
            items.append((f'H1[{cond}]', r['p'], r))
    for key, r in payload['H2']['results'].items():
        if r.get('p') is not None:
            items.append((f'H2[{key}]', r['p'], r))
    kw = payload['H3']['kruskal']
    if kw.get('p') is not None:
        items.append(('H3[kruskal]', kw['p'], kw))
    for pr in payload['H3']['dunn_posthoc']['pairs']:
        items.append((f"H3[Dunn:{pr['pair']}]", pr['p_bonferroni'], pr))
    h4 = payload['H4'].get('wilcoxon')
    if isinstance(h4, dict) and h4.get('p') is not None:
        items.append(('H4[wilcoxon]', h4['p'], h4))
    sp = payload['H5']['spearman_overall']
    if sp.get('p') is not None:
        items.append(('H5[spearman_overall]', sp['p'], sp))
    for cond, sp_c in payload['H5']['spearman_per_condition'].items():
        if sp_c.get('p') is not None:
            items.append((f'H5[spearman_{cond}]', sp_c['p'], sp_c))
    mw = payload['H5']['mann_whitney_green_vs_notgreen']
    if mw.get('p') is not None:
        items.append(('H5[MW_green_vs_notgreen]', mw['p'], mw))
    for cond, r in payload['H6']['results'].items():
        if r.get('p') is not None and np.isfinite(r['p']):
            items.append((f'H6[{cond}]', r['p'], r))
    return items


def _apply_fdr(payload: dict) -> dict:
    items = _collect_pvalues(payload)
    if not items:
        return {'n_tests': 0}
    labels = [lbl for lbl, _, _ in items]
    pvals = [p for _, p, _ in items]
    reject, p_fdr, _, _ = multipletests(pvals, alpha=ALPHA, method='fdr_bh')
    summary = []
    for (label, p_raw, container), p_adj, rej in zip(items, p_fdr, reject):
        container['p_fdr'] = round(float(p_adj), 6)
        container['fdr_significant'] = bool(rej)
        summary.append({'test': label, 'p_raw': round(float(p_raw), 6),
                       'p_fdr': round(float(p_adj), 6), 'sig_fdr_005': bool(rej)})
    return {'n_tests': len(
        items), 'method': 'Benjamini-Hochberg FDR (statsmodels.fdr_bh)', 'alpha': ALPHA, 'items': summary}


def _render_md(payload: dict) -> str:
    md: list[str] = ['# 5.2 Testy hipotez\n']
    md.append('Wszystkie testy nieparametryczne (rozklady nie sa normalne, p<0,05 w Shapiro-Wilka, sekcja 5.1). Poziom istotnosci alpha=0,05. Korekta Bonferroniego stosowana przy testach post-hoc.\n')
    md.append('## H1 - Semantic equivalence (semantic_score vs 8)\n')
    md.append("H0: median(semantic_score) >= 8 (model osiaga prog wysokiej rownowaznosci). H1: median < 8. Wilcoxon one-sample, `alternative='less'`. Odrzucenie H0 = model NIE osiaga progu.\n")
    h1 = payload['H1']
    md.append('| condition | n | median | stat | p | p_fdr | reject H0? |')
    md.append('|---|---|---|---|---|---|---|')
    for cond, r in h1['results'].items():
        rej = 'tak' if r.get('fdr_significant') else 'nie'
        med = r.get('median', '-')
        md.append(
            f"| {cond} | {r['n']} | {med} | {r['stat']} | {r['p']} | {r.get('p_fdr', '-')} | {rej} |")
    md.append('')
    md.append('## H2 - AI vs traditional (ΔCC)\n')
    md.append('Paired Wilcoxon na delta_cc dla tych samych probek (model AI vs T).\n')
    h2 = payload['H2']
    md.append('| comparison | n_pairs | median_diff | stat | p | p_fdr | r | reject H0? |')
    md.append('|---|---|---|---|---|---|---|---|')
    for k, r in h2['results'].items():
        rej = 'tak' if r.get('fdr_significant') else 'nie'
        md.append(
            f"| {k} | {r['n_pairs']} | {r.get('median_diff', '-')} | {r['stat']} | {r['p']} | {r.get('p_fdr', '-')} | {r.get('effect_r', '-')} | {rej} |")
    md.append('')
    md.append('## H3 - Roznice miedzy modelami AI (A, G, C) na ΔCC\n')
    h3 = payload['H3']
    kw = h3['kruskal']
    md.append(
        f"**Kruskal-Wallis:** H={kw['H']}, p={kw['p']}, p_fdr={kw.get('p_fdr', '-')}, epsilon^2={kw.get('epsilon_sq', '-')}, n={kw['n_total']}, k={kw['k']}.\n")
    md.append(
        f"Post-hoc: {h3['dunn_posthoc'].get('method', '-')} (Dunn 1964 z rangami z polaczonej proby, korekta Bonferroniego):\n")
    md.append('| pair | n_a | n_b | p_bonferroni | p_fdr | sig FDR 0.05? |')
    md.append('|---|---|---|---|---|---|')
    for pr in h3['dunn_posthoc']['pairs']:
        md.append(
            f"| {pr['pair']} | {pr['n_a']} | {pr['n_b']} | {pr['p_bonferroni']} | {pr.get('p_fdr', '-')} | {('tak' if pr.get('fdr_significant') else 'nie')} |")
    md.append('')
    md.append('## H4 - Narzut CI/CD (baseline vs arp)\n')
    h4 = payload['H4']
    if 'error' in h4:
        md.append(f"BLAD: {h4['error']}\n")
    else:
        md.append(
            f"Median baseline: {h4['median_baseline_s']} s, median ARP: {h4['median_arp_s']} s, median overhead: {h4['median_overhead_s']} s ({h4['n_commits']} commitow).\n")
        w = h4['wilcoxon']
        rej = 'tak' if w['p'] is not None and w['p'] < ALPHA else 'nie'
        md.append(
            f"Wilcoxon paired: n_pairs={w['n_pairs']}, median_diff={w.get('median_diff', '-')}, p={w['p']}, r={w.get('effect_r', '-')}, reject H0={rej}.\n")
    md.append('## H5 - LLM-judge vs faktyczne testy (KLUCZOWY WYNIK)\n')
    h5 = payload['H5']
    sp = h5['spearman_overall']
    md.append(
        f"**Spearman (overall):** rho={sp['rho']}, p={sp['p']}, n={sp['n']}.\nWartosc bliska 0 wspiera teze: LLM-judge ocenia kod **nieskorelowanie** z faktycznym pass rate testow.\n")
    md.append('Per warunek:\n')
    md.append('| condition | n | rho | p |')
    md.append('|---|---|---|---|')
    for cond, sp_c in h5['spearman_per_condition'].items():
        md.append(f"| {cond} | {sp_c['n']} | {sp_c['rho']} | {sp_c['p']} |")
    mw = h5['mann_whitney_green_vs_notgreen']
    md.append(
        f"\n**Mann-Whitney (quality_score: testy zielone vs nie):** n_green={mw.get('n_green', '-')}, n_notgreen={mw.get('n_notgreen', '-')}, median_green={mw.get('median_green', '-')}, median_notgreen={mw.get('median_notgreen', '-')}, p={mw.get('p', '-')}.\nBrak istotnej roznicy = LLM-judge nie potrafi rozroznic semantycznie poprawnych od bledynych refaktoryzacji.\n")
    md.append('## H6 - Accept rate v1 (Faza 4+4B) vs v2 (Faza 4C)\n')
    md.append('Test Fishera 2x2 (accepted/rejected w v1 vs v2). Spodziewamy drastycznej roznicy bo v2 dodalo bramke testowa.\n')
    md.append('| cond | a1 | r1 | a2 | r2 | OR | p | p_fdr | sig FDR? |')
    md.append('|---|---|---|---|---|---|---|---|---|')
    for cond, r in payload['H6']['results'].items():
        t = r['table']
        md.append(
            f"| {cond} | {t[0][0]} | {t[0][1]} | {t[1][0]} | {t[1][1]} | {r['odds_ratio']} | {r['p']} | {r.get('p_fdr', '-')} | {('tak' if r.get('fdr_significant') else 'nie')} |")
    mt = payload.get('multiple_testing', {})
    if mt.get('items'):
        md.append('\n## Korekta multiple-testing (Benjamini-Hochberg FDR)\n')
        md.append(
            f"Liczba testow w rodzinie: {mt['n_tests']}. Metoda: `{mt['method']}`. Alpha = {mt['alpha']}.\n")
        md.append('| test | p_raw | p_fdr | sig FDR 0.05? |')
        md.append('|---|---|---|---|')
        for it in mt['items']:
            md.append(
                f"| {it['test']} | {it['p_raw']} | {it['p_fdr']} | {('tak' if it['sig_fdr_005'] else 'nie')} |")
        md.append('')
    return '\n'.join(md) + '\n'


def run() -> dict:
    v1 = load_v1()
    v2 = load_v2(applied_only=True)
    payload = {
        'H1': H1_semantic_equivalence(v2),
        'H2': H2_AI_vs_T(v2),
        'H3': H3_AI_models(v2),
        'H4': H4_cicd_overhead(),
        'H5': H5_judge_vs_tests(v2),
        'H6': H6_accept_v1_vs_v2(
            v1,
            v2)}
    payload['multiple_testing'] = _apply_fdr(payload)
    write_summary('hypothesis_tests', payload)
    out_md = ANALYSIS_DIR / 'hypothesis_tests.md'
    out_md.write_text(_render_md(payload), encoding='utf-8')
    print(f"[hypothesis] summary -> {ANALYSIS_DIR / 'hypothesis_tests.json'}")
    print(f'[hypothesis] report  -> {out_md}')
    print('\n=== H5 (key result) ===')
    print(payload['H5']['spearman_overall'])
    print(payload['H5']['mann_whitney_green_vs_notgreen'])
    return payload


if __name__ == '__main__':
    run()
