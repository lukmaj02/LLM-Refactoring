from __future__ import annotations
from scripts.analysis.judge_retest_analysis import icc21, icc_ci, kappa_w
from scripts.analysis._dataio import ANALYSIS_DIR, _connect, load_v2
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
OUT = ANALYSIS_DIR / 'judge_cross.md'
DIMS = ['quality_score', 'semantic_score', 'solid_score', 'dry_score', 'kiss_score']


def main() -> None:
    v2 = load_v2()
    with _connect() as con:
        ja = pd.read_sql_query('SELECT * FROM judge_retest_A', con)
    base = v2[['sample_id', 'condition', 'pass_ratio', 'tests_green_strict', *DIMS]]
    m = base.merge(ja, on=['sample_id', 'condition'], suffixes=('_g', '_a'))
    lines = []
    w = lines.append
    w('# Sedzia miedzyrodzinny: GPT-4o vs Gemini (Etap 7.3)')
    w('')
    w(f'n = {len(m)} par; sedzia A = GPT-4o ocenia te same artefakty, ktore')
    w('w eksperymencie glownym ocenil sedzia G = Gemini 2.5 Flash.')
    w('')
    w('## Zgodnosc miedzy sedziami (ICC(2,1), kappa_w)')
    w('')
    w('| Wymiar | ICC(2,1) | 95% CI | kappa_w | sr. |roznica| |')
    w('|---|---|---|---|---|')
    for d in DIMS:
        a = m[f'{d}_g'].to_numpy(float)
        b = m[f'{d}_a'].to_numpy(float)
        mask = ~(np.isnan(a) | np.isnan(b))
        a, b = (a[mask], b[mask])
        icc = icc21(a, b)
        lo, hi = icc_ci(a, b, n_boot=2000)
        w(f'| {d} | {icc:.3f} | [{lo:.2f}; {hi:.2f}] | {kappa_w(a, b):.3f} | {np.abs(b - a).mean():.2f} |')
    w('')
    w('## Trafnosc sedziego GPT-4o wzgledem testow')
    w('')
    sub = m.dropna(subset=['quality_score_a', 'pass_ratio'])
    rho, p = stats.spearmanr(sub['quality_score_a'], sub['pass_ratio'])
    w(f'* Spearman quality(GPT-4o) vs pass_ratio: rho = {rho:.3f}, p = {p:.3f}, n = {len(sub)}')
    sem = m.dropna(subset=['semantic_score_a', 'pass_ratio'])
    rho2, p2 = stats.spearmanr(sem['semantic_score_a'], sem['pass_ratio'])
    w(f'* Spearman semantic(GPT-4o) vs pass_ratio: rho = {rho2:.3f}, p = {p2:.3f}, n = {len(sem)}')
    w('')
    w('## Opisowo (mediany ocen)')
    w('')
    for d in DIMS:
        w(f"* {d}: Gemini med={m[f'{d}_g'].median():.1f}, GPT-4o med={m[f'{d}_a'].median():.1f}")
    w('')
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'OK -> {OUT}')


if __name__ == '__main__':
    main()
