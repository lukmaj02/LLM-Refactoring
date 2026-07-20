from __future__ import annotations
from scripts.analysis._dataio import ANALYSIS_DIR, _connect, load_v2
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
OUT = ANALYSIS_DIR / 'rerun_gate.md'
LLM = ['A', 'G', 'C']
ALL = ['T', 'A', 'G', 'C']


def wilson(k, n):
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(k, n, alpha=0.05, method='wilson')
    return (100 * lo, 100 * hi)


def fset(s):
    return set((x for x in (s or '').split(';') if x))


def main() -> None:
    with _connect() as con:
        rr = pd.read_sql_query('SELECT * FROM test_gate_rerun', con)
    v2 = load_v2()
    v2['gate_struct_ok'] = v2['rejection_reason'].isna(
    ) | v2['rejection_reason'].str.startswith('test_failure').fillna(False)
    struct_ok = {(r.sample_id, r.condition): bool(r.gate_struct_ok) for r in v2.itertuples()}
    base = rr[rr.condition == 'BASE'].set_index('sample_id')
    lines = []
    w = lines.append
    w('# Przeliczenie bramki testowej w naprawionym srodowisku (Etap 9)')
    w('')
    w(f'Rekordow w test_gate_rerun: {len(rr)}; migawek z linia bazowa: {len(base)}.')
    w('')
    w('## 1. Linia bazowa po naprawie srodowiska (BASE, kod niezmodyfikowany)')
    w('')
    clean = base[(base.failed == 0) & (base.errors == 0) & (base.timeout == 0)]
    w(f'* migawki z czysta linia bazowa: {len(clean)}/{len(base)} ({100 * len(clean) / max(len(base), 1):.1f}%)')
    per_repo = {}
    for sid, row in base.iterrows():
        repo = sid.split('_')[0]
        per_repo.setdefault(repo, [0, 0])
        per_repo[repo][1] += 1
        if row.failed == 0 and row.errors == 0 and (row.timeout == 0):
            per_repo[repo][0] += 1
    for repo, (k, n) in sorted(per_repo.items()):
        w(f'  * {repo}: {k}/{n}')
    dirty = base[(base.failed > 0) | (base.errors > 0)]
    if len(dirty):
        w('* migawki z niezaliczonymi testami bazowo (id testow):')
        for sid, row in dirty.iterrows():
            w(f'  * {sid}: {row.failed_ids[:160]}')
    w('')
    w('### Efektywna liczba testow (zielone bazowo = faktyczna bramka)')
    w('')
    base_eff = base.copy()
    base_eff['repo'] = [s.split('_')[0] for s in base_eff.index]
    for repo, g in base_eff.groupby('repo'):
        w(f'* {repo}: mediana {g.passed.median():.0f} testow zielonych bazowo na migawke (min {g.passed.min():.0f}, max {g.passed.max():.0f})')
    zero = base_eff[base_eff.passed == 0]
    if len(zero):
        w(f"* UWAGA: migawki bez ani jednego testu zielonego bazowo (walidacja bezsilna): {', '.join(zero.index)}")
    w('')
    w('## 2. Bramka testowa per warunek (artefakty z 4C, bez -x)')
    w('')
    w('| Warunek | n par z BASE | testy czyste (strict) | regresje tozsamosciowe (nowe niezaliczone vs BASE) | CI Wilsona regresji |')
    w('|---|---|---|---|---|')
    reg_details = []
    summary = {}
    for cond in ALL:
        sub = rr[rr.condition == cond]
        k_clean = k_reg = n = 0
        for row in sub.itertuples():
            if row.sample_id not in base.index or row.patch_ok == 0:
                continue
            b = base.loc[row.sample_id]
            n += 1
            if row.failed == 0 and row.errors == 0 and (row.timeout == 0):
                k_clean += 1
            new_fail = fset(row.failed_ids) - fset(b.failed_ids)
            if row.timeout == 1:
                new_fail = {'TIMEOUT'}
            if new_fail:
                k_reg += 1
                reg_details.append((cond, row.sample_id, sorted(new_fail)))
        lo, hi = wilson(k_reg, n) if n else (0, 0)
        w(f'| {cond} | {n} | {k_clean} | {k_reg} | [{lo:.1f}; {hi:.1f}] |')
        summary[cond] = (n, k_clean, k_reg)
    w('')
    if reg_details:
        w('### Regresje tozsamosciowe (szczegoly)')
        w('')
        for cond, sid, tests in reg_details:
            w(f"* {cond} x {sid}: {'; '.join(tests)[:220]}")
        w('')
    w('## 3. Nowa kaskada: akceptacja koncowa (bramki strukturalne z 4C + bramka testowa po naprawie)')
    w('')
    w('| Warunek | strict (testy czyste) | wzgledem linii bazowej (brak nowych niezaliczonych) |')
    w('|---|---|---|')
    for cond in ALL:
        sub = rr[rr.condition == cond]
        acc_strict = acc_base = 0
        for row in sub.itertuples():
            if row.sample_id not in base.index or row.patch_ok == 0:
                continue
            if not struct_ok.get((row.sample_id, cond), False):
                continue
            b = base.loc[row.sample_id]
            if row.timeout == 0 and row.failed == 0 and (row.errors == 0):
                acc_strict += 1
            new_fail = fset(row.failed_ids) - fset(b.failed_ids)
            if row.timeout == 0 and (not new_fail):
                acc_base += 1
        lo1, hi1 = wilson(acc_strict, 105)
        lo2, hi2 = wilson(acc_base, 105)
        w(f'| {cond} | {acc_strict}/105 = {100 * acc_strict / 105:.1f}% [{lo1:.1f}; {hi1:.1f}] | {acc_base}/105 = {100 * acc_base / 105:.1f}% [{lo2:.1f}; {hi2:.1f}] |')
    w('')
    with _connect() as con:
        try:
            vd = pd.read_sql_query('SELECT * FROM regression_verdicts', con)
        except Exception:
            vd = None
    if vd is not None and len(vd):
        w('## 4. Werdykty weryfikacji celowanej (izolowane przebiegi oflagowanych testow)')
        w('')
        w('| Warunek | oflagowane | potwierdzone | niereprodukowalne | niestabilne srodowiskowo | potwierdzone /105 | CI Wilsona |')
        w('|---|---|---|---|---|---|---|')
        verdict_map = {(r.sample_id, r.condition): r.verdict for r in vd.itertuples()}
        for cond in ALL:
            sub = vd[vd.condition == cond]
            n_fl = len(sub)
            n_c = (sub.verdict == 'confirmed').sum()
            n_nr = (sub.verdict == 'not_reproduced').sum()
            n_env = (sub.verdict == 'env_unstable').sum()
            lo, hi = wilson(n_c, 105)
            w(f'| {cond} | {n_fl} | {n_c} | {n_nr} | {n_env} | {100 * n_c / 105:.1f}% | [{lo:.1f}; {hi:.1f}] |')
        w('')
        w('## 5. OSTATECZNA akceptacja: bramki strukturalne + brak potwierdzonej regresji wzgledem linii bazowej')
        w('')
        w('| Warunek | akceptacja | CI Wilsona |')
        w('|---|---|---|')
        for cond in ALL:
            sub = rr[rr.condition == cond]
            acc = 0
            for row in sub.itertuples():
                if row.sample_id not in base.index or row.patch_ok == 0:
                    continue
                if not struct_ok.get((row.sample_id, cond), False):
                    continue
                v = verdict_map.get((row.sample_id, cond))
                if v == 'confirmed':
                    continue
                acc += 1
            lo, hi = wilson(acc, 105)
            w(f'| {cond} | {acc}/105 = {100 * acc / 105:.1f}% | [{lo:.1f}; {hi:.1f}] |')
        w('')
        w('### Potwierdzone regresje per para (do tabeli/aneksu)')
        w('')
        for r in vd[vd.verdict == 'confirmed'].sort_values(['condition', 'sample_id']).itertuples():
            w(f"* {r.condition} x {r.sample_id}: {r.n_flagged} test(y); np. {(r.detail or '').split(';')[0]}")
        w('')
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'OK -> {OUT}')


if __name__ == '__main__':
    main()
