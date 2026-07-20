from __future__ import annotations
from _dataio import ANALYSIS_DIR, FIGURES_DIR, load_v2, write_summary
import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
matplotlib.use('Agg')
sys.path.insert(0, str(Path(__file__).resolve().parent))
VARIABLES = (
    'cc_before',
    'mi_before',
    'delta_cc',
    'delta_mi',
    'changed_pct',
    'quality_score',
    'solid_score',
    'dry_score',
    'kiss_score',
    'semantic_score',
    'pass_ratio',
    'tests_failed',
    'response_time_s',
    'tokens_in',
    'tokens_out')


def _spearman(a: pd.Series, b: pd.Series) -> tuple[float | None, float | None, int]:
    df = pd.concat([a, b], axis=1).dropna()
    if len(df) < 5 or df.iloc[:, 0].nunique() < 2 or df.iloc[:, 1].nunique() < 2:
        return (None, None, int(len(df)))
    res = stats.spearmanr(df.iloc[:, 0], df.iloc[:, 1])
    return (float(res.statistic), float(res.pvalue), int(len(df)))


def correlation_matrix(
        df: pd.DataFrame, columns) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rho = pd.DataFrame(index=columns, columns=columns, dtype=float)
    pval = pd.DataFrame(index=columns, columns=columns, dtype=float)
    nmat = pd.DataFrame(index=columns, columns=columns, dtype=int)
    for a in columns:
        for b in columns:
            if a not in df.columns or b not in df.columns:
                continue
            r, p, n = _spearman(df[a], df[b])
            rho.loc[a, b] = r if r is not None else np.nan
            pval.loc[a, b] = p if p is not None else np.nan
            nmat.loc[a, b] = n
    return (rho, pval, nmat)


def targeted_pairs(df: pd.DataFrame) -> dict:
    pairs = [
        ('changed_pct',
         'quality_score'),
        ('cc_before',
         'delta_cc'),
        ('cc_before',
         'delta_mi'),
        ('quality_score',
         'pass_ratio'),
        ('semantic_score',
         'pass_ratio'),
        ('response_time_s',
         'delta_cc'),
        ('tokens_in',
         'quality_score'),
        ('changed_pct',
         'pass_ratio')]
    out: dict[str, dict] = {}
    for a, b in pairs:
        key = f'{a}__vs__{b}'
        r, p, n = _spearman(df[a], df[b])
        per_cond = {}
        for cond, sub in df.groupby('condition'):
            r_c, p_c, n_c = _spearman(sub[a], sub[b])
            per_cond[str(cond)] = {'n': n_c, 'rho': round(
                r_c, 4) if r_c is not None else None, 'p': round(p_c, 6) if p_c is not None else None}
        out[key] = {
            'global': {
                'n': n, 'rho': round(
                    r, 4) if r is not None else None, 'p': round(
                    p, 6) if p is not None else None}, 'per_condition': per_cond}
    return out


def plot_heatmap(rho: pd.DataFrame, pval: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 9))
    mask = rho.isna()
    data = rho.astype(float).values
    im = ax.imshow(data, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    ax.set_xticks(range(len(rho.columns)))
    ax.set_yticks(range(len(rho.index)))
    ax.set_xticklabels(rho.columns, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(rho.index, fontsize=9)
    for i in range(rho.shape[0]):
        for j in range(rho.shape[1]):
            v = data[i, j]
            if np.isnan(v):
                continue
            p = pval.iloc[i, j]
            stars = ''
            if p is not None and (not np.isnan(p)):
                if p < 0.001:
                    stars = '***'
                elif p < 0.01:
                    stars = '**'
                elif p < 0.05:
                    stars = '*'
            color = 'white' if abs(v) > 0.5 else 'black'
            ax.text(j, i, f'{v:.2f}{stars}', ha='center', va='center', color=color, fontsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    cbar.set_label('Spearman ρ', fontsize=10)
    ax.set_title(
        'Macierz korelacji Spearmana (Faza 4C, patch_applied=1)\n* p<0.05, ** p<0.01, *** p<0.001',
        fontsize=11)
    fig.tight_layout()
    out = FIGURES_DIR / 'correlations_heatmap_v2.png'
    fig.savefig(out, dpi=180, bbox_inches='tight')
    plt.close(fig)
    return out


def render_md(payload: dict) -> str:
    md = ['# 5.4 Korelacje Spearmana (Faza 4C)\n']
    md.append('Wszystkie obliczenia na zbiorze `experiment_results_v2` z `patch_applied=1`. Spearman dlatego, ze EDA wykazalo brak normalnosci.\n')
    md.append('## Targetowane pary zmiennych\n')
    md.append('| para | scope | n | rho | p | sig 0.05 |')
    md.append('|---|---|---|---|---|---|')
    for key, data in payload['targeted'].items():
        g = data['global']
        sig = 'tak' if g['p'] is not None and g['p'] < 0.05 else 'nie'
        md.append(f"| **{key}** | global | {g['n']} | {g['rho']} | {g['p']} | {sig} |")
        for cond, r in data['per_condition'].items():
            sig_c = 'tak' if r['p'] is not None and r['p'] < 0.05 else 'nie'
            md.append(f"| {key} | cond={cond} | {r['n']} | {r['rho']} | {r['p']} | {sig_c} |")
    md.append('')
    md.append('## Interpretacja kluczowych wynikow\n')
    md.append("- **`quality_score` vs `pass_ratio`**: oczekiwana wysoka korelacja, gdyby LLM-judge poprawnie ocenial semantyke. Wartosc bliska 0 = potwierdzenie tezy pracy.\n- **`changed_pct` vs `quality_score`**: czy modele dostaja wyzsze oceny za 'wiekszy' refaktoring? Dodatnia korelacja = ryzyko bias (judge nagradza zmiane, nie poprawe).\n- **`cc_before` vs `delta_cc`**: silna dodatnia = regresja ku sredniej, klasyczny efekt; wieksze CC -> wieksza redukcja.\n- **`semantic_score` vs `pass_ratio`**: poddyrektywa kluczowego wyniku - czy konkretny wymiar 'Semantic Equivalence' lepiej koreluje z testami niz `quality_score`?\n")
    return '\n'.join(md) + '\n'


def run() -> dict:
    v2 = load_v2(applied_only=True)
    rho, pval, _ = correlation_matrix(v2, list(VARIABLES))
    payload = {
        'global_matrix_rho': rho.round(4).to_dict(),
        'global_matrix_p': pval.round(6).to_dict(),
        'targeted': targeted_pairs(v2)}
    write_summary('correlations', payload)
    fig = plot_heatmap(rho, pval)
    out_md = ANALYSIS_DIR / 'correlations.md'
    out_md.write_text(render_md(payload), encoding='utf-8')
    print(f"[correlations] summary -> {ANALYSIS_DIR / 'correlations.json'}")
    print(f'[correlations] report  -> {out_md}')
    print(f'[correlations] heatmap -> {fig}')
    print('\nKey global pairs:')
    for key in ('changed_pct__vs__quality_score', 'cc_before__vs__delta_cc',
                'quality_score__vs__pass_ratio', 'semantic_score__vs__pass_ratio'):
        g = payload['targeted'][key]['global']
        print(f"  {key}: rho={g['rho']}, p={g['p']}, n={g['n']}")
    return payload


if __name__ == '__main__':
    run()
