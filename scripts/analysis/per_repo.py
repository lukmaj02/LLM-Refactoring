from __future__ import annotations
from _dataio import ANALYSIS_DIR, load_v2, write_summary
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parent.parent.parent


def attach_repo(df: pd.DataFrame) -> pd.DataFrame:
    if 'repo' in df.columns and df['repo'].notna().any():
        return df
    with (ROOT / 'data' / 'snapshots' / 'index.json').open(encoding='utf-8') as fh:
        idx = pd.DataFrame(json.load(fh))[['sample_id', 'repo']]
    return df.merge(idx, on='sample_id', how='left')


def _cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 or len(b) == 0:
        return float('nan')
    greater = sum((1 for x in a for y in b if x > y))
    less = sum((1 for x in a for y in b if x < y))
    total = len(a) * len(b)
    return (greater - less) / total


def _paired_wilcoxon(a, b) -> dict:
    pairs = [(x, y) for x, y in zip(a, b) if not (pd.isna(x) or pd.isna(y))]
    if len(pairs) < 5:
        return {'n_pairs': int(len(pairs)), 'p': None}
    x, y = zip(*pairs)
    try:
        res = stats.wilcoxon(np.asarray(x), np.asarray(y), alternative='two-sided')
    except ValueError:
        return {'n_pairs': int(len(pairs)), 'p': None, 'note': 'no differences'}
    diffs = np.asarray(x) - np.asarray(y)
    return {'n_pairs': int(len(pairs)), 'median_diff': round(
        float(np.median(diffs)), 3), 'p': round(float(res.pvalue), 6)}


def per_repo_analysis(df: pd.DataFrame) -> dict:
    out: dict[str, dict] = {}
    for repo, sub in df.groupby('repo'):
        if pd.isna(repo):
            continue
        applied = sub[sub['patch_applied'] == 1]
        pivot = applied.pivot_table(index='sample_id', columns='condition', values='delta_cc')
        h2_pairs = {}
        cliffs = {}
        for c in ('A', 'G', 'C'):
            if c in pivot.columns and 'T' in pivot.columns:
                h2_pairs[f'{c}_vs_T'] = _paired_wilcoxon(pivot[c].tolist(), pivot['T'].tolist())
            a = applied[applied['condition'] == c]['delta_cc'].dropna().to_numpy()
            t = applied[applied['condition'] == 'T']['delta_cc'].dropna().to_numpy()
            cliffs[f'{c}_vs_T'] = round(_cliffs_delta(a, t), 4)
        h5_sub = applied[(applied['tests_targeted'].fillna(0) > 0) &
                         applied['quality_score'].notna() & applied['pass_ratio'].notna()]
        if len(h5_sub) >= 5:
            r_h5, p_h5 = stats.spearmanr(h5_sub['quality_score'], h5_sub['pass_ratio'])
            h5 = {'n': int(len(h5_sub)), 'rho': round(float(r_h5), 4), 'p': round(float(p_h5), 6)}
        else:
            h5 = {'n': int(len(h5_sub)), 'rho': None, 'p': None}
        median_pass = {c: round(float(applied[applied['condition'] == c]['pass_ratio'].dropna().median(
        )), 4) if applied[applied['condition'] == c]['pass_ratio'].notna().any() else None for c in ('T', 'A', 'G', 'C')}
        out[str(repo)] = {'n_total': int(len(sub)),
                          'n_applied': int(len(applied)),
                          'applied_per_condition': applied.groupby('condition').size().to_dict(),
                          'h2_paired_wilcoxon': h2_pairs,
                          'cliffs_delta_vs_T_on_delta_cc': cliffs,
                          'h5_spearman_quality_vs_pass': h5,
                          'median_pass_ratio': median_pass}
    return out


def kruskal_repos_in_A(df: pd.DataFrame) -> dict:
    sub = df[(df['condition'] == 'A') & (df['patch_applied'] == 1)]
    groups = [sub[sub['repo'] == r]['delta_cc'].dropna().to_numpy()
              for r in sorted(sub['repo'].dropna().unique())]
    sizes = [int(len(g)) for g in groups]
    if min(sizes) < 3:
        return {'sizes': sizes, 'H': None, 'p': None}
    res = stats.kruskal(*groups)
    return {'sizes_per_repo': sizes, 'repos': sorted(sub['repo'].dropna().unique().tolist()), 'H': round(
        float(res.statistic), 3), 'p': round(float(res.pvalue), 6)}


def render_md(payload: dict) -> str:
    md = ['# 5.A4 Per-repozytorium - zewnetrzna walidacja\n']
    md.append('Czy efekty zaobserwowane globalnie powtarzaja sie w kazdym z trzech repozytoriow? Test sprawdza, czy wyniki nie sa napedzane wylacznie przez jeden dataset.\n')
    md.append('## Liczebnosci per repo / warunek (applied=1)\n')
    md.append('| repo | T | A | G | C | total_applied |')
    md.append('|---|---|---|---|---|---|')
    for repo, r in payload['per_repo'].items():
        ap = r['applied_per_condition']
        md.append(
            f"| {repo} | {ap.get('T', 0)} | {ap.get('A', 0)} | {ap.get('G', 0)} | {ap.get('C', 0)} | {r['n_applied']} |")
    md.append('\n## H2 - paired Wilcoxon delta_cc vs T (per repo)\n')
    md.append('| repo | comparison | n_pairs | median_diff | p |')
    md.append('|---|---|---|---|---|')
    for repo, r in payload['per_repo'].items():
        for cmp, w in r['h2_paired_wilcoxon'].items():
            md.append(
                f"| {repo} | {cmp} | {w.get('n_pairs', '-')} | {w.get('median_diff', '-')} | {w.get('p', '-')} |")
    md.append('\n## H5 - Spearman quality_score vs pass_ratio (per repo)\n')
    md.append('| repo | n | rho | p | replicates global signal? |')
    md.append('|---|---|---|---|---|')
    for repo, r in payload['per_repo'].items():
        h5 = r['h5_spearman_quality_vs_pass']
        same_sign = 'tak (slabe/brak)' if h5['rho'] is not None and abs(h5['rho']
                                                                        ) < 0.2 else 'rozne'
        md.append(f"| {repo} | {h5['n']} | {h5['rho']} | {h5['p']} | {same_sign} |")
    md.append("\n## Cliff's delta na delta_cc (AI vs T) per repo\n")
    md.append('| repo | A_vs_T | G_vs_T | C_vs_T |')
    md.append('|---|---|---|---|')
    for repo, r in payload['per_repo'].items():
        c = r['cliffs_delta_vs_T_on_delta_cc']
        md.append(
            f"| {repo} | {c.get('A_vs_T', '-')} | {c.get('G_vs_T', '-')} | {c.get('C_vs_T', '-')} |")
    md.append('\n## Mediana pass_ratio per repo x warunek\n')
    md.append('| repo | T | A | G | C |')
    md.append('|---|---|---|---|---|')
    for repo, r in payload['per_repo'].items():
        m = r['median_pass_ratio']
        md.append(
            f"| {repo} | {m.get('T', '-')} | {m.get('A', '-')} | {m.get('G', '-')} | {m.get('C', '-')} |")
    md.append('\n## Czy ΔCC w warunku A rozni sie miedzy repo?\n')
    k = payload['kruskal_repos_in_A']
    md.append(
        f"Kruskal-Wallis: H={k.get('H', '-')}, p={k.get('p', '-')}, sizes={k.get('sizes_per_repo', '-')}.\nRepozytoria: {k.get('repos', '-')}.\n")
    md.append('\n## Interpretacja\n')
    md.append('- Jesli kierunek efektu H2 (delta_cc > 0 dla AI vs T) jest spojny we wszystkich repo - efekt jest **zewnetrznie wazny**.\n- Jesli H5 (brak korelacji judge↔testy) replikuje sie w kazdym repo, wynik nie jest artefaktem jednego datasetu.\n- Roznice w accept rate i pass_ratio mowia o **trudnosci kazdego kodu** - flask/httpie/requests maja rozne style i pokrycie testowe.\n')
    return '\n'.join(md) + '\n'


def run() -> dict:
    v2 = load_v2(applied_only=False)
    v2 = attach_repo(v2)
    payload = {'per_repo': per_repo_analysis(v2), 'kruskal_repos_in_A': kruskal_repos_in_A(v2)}
    write_summary('per_repo', payload)
    out_md = ANALYSIS_DIR / 'per_repo.md'
    out_md.write_text(render_md(payload), encoding='utf-8')
    print(f"[per_repo] summary -> {ANALYSIS_DIR / 'per_repo.json'}")
    print(f'[per_repo] report  -> {out_md}')
    print('\n=== H5 per repo ===')
    for repo, r in payload['per_repo'].items():
        h5 = r['h5_spearman_quality_vs_pass']
        print(f"  {repo}: rho={h5['rho']}, p={h5['p']}, n={h5['n']}")
    return payload


if __name__ == '__main__':
    run()
