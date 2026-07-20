from __future__ import annotations
from scripts.analysis._dataio import ANALYSIS_DIR, _connect
import sys
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
OUT = ANALYSIS_DIR / 'judge_retest.md'
DIMS = ['quality_score', 'semantic_score', 'solid_score', 'dry_score', 'kiss_score']


def icc21(x: np.ndarray, y: np.ndarray) -> float:
    data = np.column_stack([x, y]).astype(float)
    n, k = data.shape
    mean_t = data.mean(axis=1)
    mean_r = data.mean(axis=0)
    grand = data.mean()
    ss_t = k * ((mean_t - grand) ** 2).sum()
    ss_r = n * ((mean_r - grand) ** 2).sum()
    ss_tot = ((data - grand) ** 2).sum()
    ss_e = ss_tot - ss_t - ss_r
    ms_t = ss_t / (n - 1)
    ms_r = ss_r / (k - 1)
    ms_e = ss_e / ((n - 1) * (k - 1))
    return (ms_t - ms_e) / (ms_t + (k - 1) * ms_e + k * (ms_r - ms_e) / n)


def icc_ci(x: np.ndarray, y: np.ndarray, n_boot: int = 5000) -> tuple[float, float]:
    rng = np.random.default_rng(42)
    n = len(x)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        try:
            vals.append(icc21(x[idx], y[idx]))
        except ZeroDivisionError:
            continue
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


def kappa_w(x: np.ndarray, y: np.ndarray, n_cat: int = 11) -> float:
    obs = np.zeros((n_cat, n_cat))
    for a, b in zip(x.astype(int), y.astype(int)):
        obs[a, b] += 1
    obs /= obs.sum()
    px, py = (obs.sum(axis=1), obs.sum(axis=0))
    exp = np.outer(px, py)
    i, j = np.indices((n_cat, n_cat))
    v = (i - j) ** 2 / (n_cat - 1) ** 2
    return 1 - (obs * v).sum() / (exp * v).sum()


def interpret_icc(v: float) -> str:
    if v < 0.5:
        return 'slaba (poor)'
    if v < 0.75:
        return 'umiarkowana (moderate)'
    if v < 0.9:
        return 'dobra (good)'
    return 'doskonala (excellent)'


def main() -> None:
    with _connect() as con:
        r2 = pd.read_sql_query('SELECT * FROM judge_retest', con)
        r1 = pd.read_sql_query(
            "SELECT sample_id, condition, solid_score, dry_score, kiss_score,\n                      semantic_score, quality_score\n               FROM experiment_results_v2 WHERE phase='4C'",
            con)
    df = r1.merge(r2, on=['sample_id', 'condition'], suffixes=('_1', '_2'))
    lines: list[str] = []
    w = lines.append
    w('# Test-retest sedziego LLM na identycznych artefaktach (Etap 2.1)')
    w('')
    w(f'n = {len(df)} par (sample_id x warunek); przebieg 1 = eksperyment glowny 4C,')
    w('przebieg 2 = ponowna ocena TYCH SAMYCH plikow kodu (skrypt run_judge_retest.py,')
    w('sedzia: Gemini 2.5 Flash, T=0,0).')
    w('')
    w('| Wymiar | ICC(2,1) | 95% CI (bootstrap) | interpretacja | kappa_w | sr. |roznica| | LoA +/- |')
    w('|---|---|---|---|---|---|---|')
    for dim in DIMS:
        a = df[f'{dim}_1'].to_numpy(float)
        b = df[f'{dim}_2'].to_numpy(float)
        mask = ~(np.isnan(a) | np.isnan(b))
        a, b = (a[mask], b[mask])
        icc = icc21(a, b)
        lo, hi = icc_ci(a, b)
        kw = kappa_w(a, b)
        diff = b - a
        loa = 1.96 * diff.std(ddof=1)
        w(f'| {dim} | {icc:.3f} | [{lo:.2f}; {hi:.2f}] | {interpret_icc(icc)} | {kw:.3f} | {np.abs(diff).mean():.2f} | {loa:.2f} |')
    w('')
    d = df['quality_score_2'] - df['quality_score_1']
    w(f'Bland-Altman (quality_score): srednia roznica = {d.mean():.2f}, granice zgodnosci [{d.mean() - 1.96 * d.std(ddof=1):.2f}; {d.mean() + 1.96 * d.std(ddof=1):.2f}] na skali 0-10.')
    w('')
    w(f'Zgodnosc idealna (identyczna ocena quality): {(d == 0).mean() * 100:.1f}% par; roznica >= 2 pkt: {(d.abs() >= 2).mean() * 100:.1f}%.')
    w('')
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text('\n'.join(lines), encoding='utf-8')
    print(f'OK -> {OUT}')


if __name__ == '__main__':
    main()
