# Faza 4C - raport porownawczy v1 (Faza 4 + 4B) vs v2 (single-pass)

Wygenerowane automatycznie przez `scripts/analyze_4c.py`. Tabela v2 pochodzi z `experiment_results_v2` (single-pass, `temperature=0.0`, walidacja testowa, LLM-judge na tym samym pliku). Tabela v1 zawiera dane historyczne z Fazy 4 + 4B.

## Wyniki v2 (Faza 4C)

### Per-condition v2

| condition | n | patch_applied | patch_accepted | accept_rate | samples_with_tests | tests_green_strict | tests_green_relaxed_1fail | mean_pass_ratio | mean_changed_pct | mean_quality_score | mean_solid | mean_dry | mean_kiss | mean_semantic | total_cost_usd | mean_response_time_s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 105 | 105 | 5 | 0.048 | 105 | 7 | 93 | 0.92 | 0.541 | 7.41 | 7.914 | 5.638 | 7.543 | 8.943 | 1.917 | 4.609 |
| C | 105 | 105 | 4 | 0.038 | 105 | 7 | 90 | 0.893 | 0.434 | 7.619 | 7.248 | 5.886 | 7.467 | 9.857 | 3.0559 | 7.052 |
| G | 105 | 75 | 2 | 0.019 | 75 | 4 | 65 | 0.931 | 0.59 | 7.147 | 7.2 | 5.88 | 7.107 | 9.053 | 0.1337 | 13.971 |
| T | 105 | 105 | 0 | 0.0 | 105 | 8 | 94 | 0.938 | 0.027 | 4.587 | 5 | 5 | 4.952 | 9.904 | 0 | 0.289 |

## Wyniki v1 (Faza 4 + 4B, historyczne)

### Per-condition v1

| condition | n | patch_applied | patch_accepted | accept_rate | mean_quality_score | mean_solid | mean_dry | mean_kiss | mean_semantic | total_cost_usd |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 105 | 105 | 81 | 0.771 | 7.602 | 7.563 | 5.641 | 7.524 | 9.223 | 0.5309 |
| C | 105 | 105 | 70 | 0.667 | 8.31 | 7.631 | 5.869 | 8.095 | 9.881 | 1.0111 |
| G | 105 | 103 | 46 | 0.438 | 7 | 7.196 | 5.49 | 7.412 | 7.647 | 0.0308 |
| K | 105 | 0 | 0 | 0.0 | - | - | - | - | - | 0 |
| T | 105 | 105 | 13 | 0.124 | - | - | - | - | - | 0 |

## Korelacja metryk z testami (v2)

```json

{
  "n_samples_with_tests": 353,
  "pearson_quality_vs_pass_ratio": -0.031,
  "mean_cc_delta": -2.793,
  "mean_mi_delta": -3.339
}

```

## Interpretacja


**Kluczowe odkrycie:** korelacja Pearsona miedzy ocena LLM-judge a faktycznym pass rate testow wynosi r = -0.031 (n=353). Wartosc bliska zera empirycznie wspiera teze, ze LLM-as-Judge **nie potrafi rzetelnie ocenic semantycznej rownowaznosci refaktoryzacji** wylacznie na podstawie tekstu kodu - mimo dawania ocen 'Semantic Equivalence' rzedu 9-10/10 wiele refaktoryzacji lamie istniejace testy regresyjne. Tylko rzeczywiste uruchomienie testow dostarcza wiarygodnej walidacji semantyki.


- `accept_rate` w v2 wymaga zgodnosci dwoch bramek: testy zielone I poprawa metryki (CC obnizenie lub MI wzrost). W v1 brakowalo bramki testowej, stad dramatyczna roznica accept rate (v1: 44-77%, v2: 2-5%).
- `mean_quality_score` w v2 to ocena LLM-judge wykonana na ZAPISANYM pliku (`refactored_code_hash` zweryfikowany) - eliminuje rozjazd niedeterminizmu z v1 (`temperature=0.2` w v1 vs `0.0` w v2).
- `tests_green_strict` (0 failed/errors) vs `tests_green_relaxed_1fail` (tolerancja 1 flaky test) - duza roznica miedzy tymi miarami sugeruje ze duzo testow w trzech repozytoriach jest sieciowo/srodowiskowo zaleznych.
- `mean_changed_pct` rzedu 0.5-0.6 (A, G, C) vs 0.03 (T) - modele AI wykonuja znaczace przeksztalcenia, T jedynie czysci kosmetycznie.
- T (autopep8 + autoflake) ma `mean_semantic = 9.9` w ocenie LLM-judge: tu judge ma racje, bo T nie zmienia logiki. Ale jego ogolna ocena (4.6) jest niska, bo nie poprawia SOLID/DRY/KISS.
- `mean_cc_delta < 0` oznacza srednie obnizenie zlozonosci cyklomatycznej.
