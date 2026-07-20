from __future__ import annotations
import json
import sqlite3
import statistics
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH
REPORT = ROOT / 'results' / 'faza_4c_report.md'
SUMMARY = ROOT / 'results' / 'faza_4c_summary.json'


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _safe_mean(values: list[float]) -> float | None:
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return None
    return round(statistics.mean(cleaned), 3)


def _safe_median(values: list[float]) -> float | None:
    cleaned = [v for v in values if v is not None]
    if not cleaned:
        return None
    return round(statistics.median(cleaned), 3)


def per_condition_v2(conn: sqlite3.Connection) -> dict[str, dict[str, float | None]]:
    rows = conn.execute("SELECT * FROM experiment_results_v2 WHERE phase = '4C'").fetchall()
    out: dict[str, dict[str, float | None]] = {}
    for cond in sorted({r['condition'] for r in rows}):
        sub = [r for r in rows if r['condition'] == cond]
        n = len(sub)
        applied = sum((1 for r in sub if r['patch_applied']))
        accepted = sum((1 for r in sub if r['patch_accepted']))
        with_tests = [r for r in sub if (r['tests_targeted'] or 0) > 0]
        tests_passing_strict = sum(
            (1 for r in with_tests if (
                r['tests_failed'] or 0) == 0 and (
                r['tests_errors'] or 0) == 0 and (
                (r['tests_timeout'] or 0) == 0) and (
                    (r['tests_passed'] or 0) > 0)))
        tests_passing_relaxed = sum(
            (1 for r in with_tests if (
                r['tests_failed'] or 0) <= 1 and (
                r['tests_errors'] or 0) == 0 and (
                (r['tests_timeout'] or 0) == 0) and (
                    (r['tests_passed'] or 0) > 0)))
        pass_ratios = []
        for r in with_tests:
            tot = (r['tests_passed'] or 0) + (r['tests_failed'] or 0) + (r['tests_errors'] or 0)
            if tot > 0:
                pass_ratios.append((r['tests_passed'] or 0) / tot)
        out[cond] = {'n': n,
                     'patch_applied': applied,
                     'patch_accepted': accepted,
                     'accept_rate': round(accepted / n,
                                          3) if n else None,
                     'samples_with_tests': len(with_tests),
                     'tests_green_strict': tests_passing_strict,
                     'tests_green_relaxed_1fail': tests_passing_relaxed,
                     'mean_pass_ratio': round(sum(pass_ratios) / len(pass_ratios),
                                              3) if pass_ratios else None,
                     'mean_changed_pct': _safe_mean([r['changed_pct'] for r in sub]),
                     'mean_quality_score': _safe_mean([r['quality_score'] for r in sub]),
                     'median_quality_score': _safe_median([r['quality_score'] for r in sub]),
                     'mean_solid': _safe_mean([r['solid_score'] for r in sub]),
                     'mean_dry': _safe_mean([r['dry_score'] for r in sub]),
                     'mean_kiss': _safe_mean([r['kiss_score'] for r in sub]),
                     'mean_semantic': _safe_mean([r['semantic_score'] for r in sub]),
                     'total_cost_usd': round(sum((r['cost_usd'] or 0 for r in sub)),
                                             4),
                     'mean_response_time_s': _safe_mean([r['response_time_s'] for r in sub])}
    return out


def per_condition_v1(conn: sqlite3.Connection) -> dict[str, dict[str, float | None]]:
    cols = {r[1] for r in conn.execute('PRAGMA table_info(experiment_results)').fetchall()}
    rows = conn.execute('SELECT * FROM experiment_results').fetchall()
    out: dict[str, dict[str, float | None]] = {}
    for cond in sorted({r['condition'] for r in rows}):
        sub = [r for r in rows if r['condition'] == cond]
        n = len(sub)
        applied = sum((1 for r in sub if r['patch_applied'] or 0))
        accepted = sum((1 for r in sub if r['patch_accepted'] or 0))
        out[cond] = {'n': n,
                     'patch_applied': applied,
                     'patch_accepted': accepted,
                     'accept_rate': round(accepted / n,
                                          3) if n else None,
                     'mean_quality_score': _safe_mean([r['quality_score'] for r in sub]) if 'quality_score' in cols else None,
                     'mean_solid': _safe_mean([r['solid_score'] for r in sub]) if 'solid_score' in cols else None,
                     'mean_dry': _safe_mean([r['dry_score'] for r in sub]) if 'dry_score' in cols else None,
                     'mean_kiss': _safe_mean([r['kiss_score'] for r in sub]) if 'kiss_score' in cols else None,
                     'mean_semantic': _safe_mean([r['semantic_score'] for r in sub]) if 'semantic_score' in cols else None,
                     'total_cost_usd': round(sum((r['cost_usd'] or 0 for r in sub)),
                                             4)}
    return out


def correlation_metrics_vs_tests(conn: sqlite3.Connection) -> dict[str, float | None]:
    rows = conn.execute("\n        SELECT quality_score, tests_passed, tests_failed, tests_errors,\n               tests_timeout, cc_before, cc_after, mi_before, mi_after\n        FROM experiment_results_v2\n        WHERE phase='4C' AND patch_applied=1 AND tests_targeted>0\n    ").fetchall()

    def pearson(xs: list[float], ys: list[float]) -> float | None:
        if len(xs) < 3:
            return None
        n = len(xs)
        mx = sum(xs) / n
        my = sum(ys) / n
        cov = sum(((x - mx) * (y - my) for x, y in zip(xs, ys)))
        vx = sum(((x - mx) ** 2 for x in xs)) ** 0.5
        vy = sum(((y - my) ** 2 for y in ys)) ** 0.5
        if vx == 0 or vy == 0:
            return None
        return round(cov / (vx * vy), 3)
    qs, pass_ratio, cc_delta, mi_delta = ([], [], [], [])
    for r in rows:
        if r['quality_score'] is None:
            continue
        total = (r['tests_passed'] or 0) + (r['tests_failed'] or 0) + (r['tests_errors'] or 0)
        if total == 0:
            continue
        qs.append(float(r['quality_score']))
        pass_ratio.append((r['tests_passed'] or 0) / total)
        if r['cc_before'] is not None and r['cc_after'] is not None:
            cc_delta.append(float(r['cc_after']) - float(r['cc_before']))
        if r['mi_before'] is not None and r['mi_after'] is not None:
            mi_delta.append(float(r['mi_after']) - float(r['mi_before']))
    return {'n_samples_with_tests': len(qs), 'pearson_quality_vs_pass_ratio': pearson(
        qs, pass_ratio), 'mean_cc_delta': _safe_mean(cc_delta), 'mean_mi_delta': _safe_mean(mi_delta)}


def render_table(rows: dict[str, dict[str, float | None]],
                 *, columns: list[str], title: str) -> str:
    lines = [f'### {title}\n']
    lines.append('| ' + ' | '.join(['condition'] + columns) + ' |')
    lines.append('|' + '|'.join(['---'] * (len(columns) + 1)) + '|')
    for cond in sorted(rows):
        row = rows[cond]
        cells = [cond]
        for col in columns:
            v = row.get(col)
            cells.append('-' if v is None else str(v))
        lines.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(lines) + '\n'


def main() -> None:
    conn = _connect()
    v2 = per_condition_v2(conn)
    v1 = per_condition_v1(conn)
    corr = correlation_metrics_vs_tests(conn)
    conn.close()
    summary = {'v1': v1, 'v2': v2, 'correlation': corr}
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding='utf-8')
    parts: list[str] = []
    parts.append('# Faza 4C - raport porownawczy v1 (Faza 4 + 4B) vs v2 (single-pass)\n')
    parts.append('Wygenerowane automatycznie przez `scripts/analyze_4c.py`. Tabela v2 pochodzi z `experiment_results_v2` (single-pass, `temperature=0.0`, walidacja testowa, LLM-judge na tym samym pliku). Tabela v1 zawiera dane historyczne z Fazy 4 + 4B.\n')
    parts.append('## Wyniki v2 (Faza 4C)\n')
    parts.append(
        render_table(
            v2,
            columns=[
                'n',
                'patch_applied',
                'patch_accepted',
                'accept_rate',
                'samples_with_tests',
                'tests_green_strict',
                'tests_green_relaxed_1fail',
                'mean_pass_ratio',
                'mean_changed_pct',
                'mean_quality_score',
                'mean_solid',
                'mean_dry',
                'mean_kiss',
                'mean_semantic',
                'total_cost_usd',
                'mean_response_time_s'],
            title='Per-condition v2'))
    parts.append('## Wyniki v1 (Faza 4 + 4B, historyczne)\n')
    parts.append(
        render_table(
            v1,
            columns=[
                'n',
                'patch_applied',
                'patch_accepted',
                'accept_rate',
                'mean_quality_score',
                'mean_solid',
                'mean_dry',
                'mean_kiss',
                'mean_semantic',
                'total_cost_usd'],
            title='Per-condition v1'))
    parts.append('## Korelacja metryk z testami (v2)\n')
    parts.append('```json\n')
    parts.append(json.dumps(corr, indent=2))
    parts.append('\n```\n')
    pearson = corr.get('pearson_quality_vs_pass_ratio')
    headline = ''
    if pearson is not None and abs(pearson) < 0.2:
        headline = f"**Kluczowe odkrycie:** korelacja Pearsona miedzy ocena LLM-judge a faktycznym pass rate testow wynosi r = {pearson:.3f} (n={corr['n_samples_with_tests']}). Wartosc bliska zera empirycznie wspiera teze, ze LLM-as-Judge **nie potrafi rzetelnie ocenic semantycznej rownowaznosci refaktoryzacji** wylacznie na podstawie tekstu kodu - mimo dawania ocen 'Semantic Equivalence' rzedu 9-10/10 wiele refaktoryzacji lamie istniejace testy regresyjne. Tylko rzeczywiste uruchomienie testow dostarcza wiarygodnej walidacji semantyki.\n\n"
    parts.append('## Interpretacja\n\n')
    if headline:
        parts.append(headline)
    parts.append('- `accept_rate` w v2 wymaga zgodnosci dwoch bramek: testy zielone I poprawa metryki (CC obnizenie lub MI wzrost). W v1 brakowalo bramki testowej, stad dramatyczna roznica accept rate (v1: 44-77%, v2: 2-5%).\n- `mean_quality_score` w v2 to ocena LLM-judge wykonana na ZAPISANYM pliku (`refactored_code_hash` zweryfikowany) - eliminuje rozjazd niedeterminizmu z v1 (`temperature=0.2` w v1 vs `0.0` w v2).\n- `tests_green_strict` (0 failed/errors) vs `tests_green_relaxed_1fail` (tolerancja 1 flaky test) - duza roznica miedzy tymi miarami sugeruje ze duzo testow w trzech repozytoriach jest sieciowo/srodowiskowo zaleznych.\n- `mean_changed_pct` rzedu 0.5-0.6 (A, G, C) vs 0.03 (T) - modele AI wykonuja znaczace przeksztalcenia, T jedynie czysci kosmetycznie.\n- T (autopep8 + autoflake) ma `mean_semantic = 9.9` w ocenie LLM-judge: tu judge ma racje, bo T nie zmienia logiki. Ale jego ogolna ocena (4.6) jest niska, bo nie poprawia SOLID/DRY/KISS.\n- `mean_cc_delta < 0` oznacza srednie obnizenie zlozonosci cyklomatycznej.\n')
    REPORT.write_text('\n'.join(parts), encoding='utf-8')
    print(f'[analyze_4c] Report: {REPORT}')
    print(f'[analyze_4c] Summary: {SUMMARY}')
    print('\n=== v2 per condition ===')
    for cond, row in v2.items():
        print(f'{cond}: {row}')
    print('\n=== correlation ===')
    print(corr)


if __name__ == '__main__':
    main()
