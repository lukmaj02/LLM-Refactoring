# 5.A4 Per-repozytorium - zewnetrzna walidacja

Czy efekty zaobserwowane globalnie powtarzaja sie w kazdym z trzech repozytoriow? Test sprawdza, czy wyniki nie sa napedzane wylacznie przez jeden dataset.

## Liczebnosci per repo / warunek (applied=1)

| repo | T | A | G | C | total_applied |
|---|---|---|---|---|---|
| flask | 35 | 35 | 25 | 35 | 130 |
| httpie | 35 | 35 | 24 | 35 | 129 |
| requests | 35 | 35 | 26 | 35 | 131 |

## H2 - paired Wilcoxon delta_cc vs T (per repo)

| repo | comparison | n_pairs | median_diff | p |
|---|---|---|---|---|
| flask | A_vs_T | 35 | 2.0 | 3.9e-05 |
| flask | G_vs_T | 25 | 1.0 | 0.000942 |
| flask | C_vs_T | 35 | 1.0 | 8.3e-05 |
| httpie | A_vs_T | 35 | 4.0 | 2e-06 |
| httpie | G_vs_T | 24 | 3.0 | 0.000128 |
| httpie | C_vs_T | 35 | 3.0 | 2e-06 |
| requests | A_vs_T | 35 | 2.0 | 1.2e-05 |
| requests | G_vs_T | 26 | 2.0 | 0.000191 |
| requests | C_vs_T | 35 | 3.0 | 2.6e-05 |

## H5 - Spearman quality_score vs pass_ratio (per repo)

| repo | n | rho | p | replicates global signal? |
|---|---|---|---|---|
| flask | 118 | -0.1983 | 0.031313 | tak (slabe/brak) |
| httpie | 116 | 0.0774 | 0.408654 | tak (slabe/brak) |
| requests | 119 | -0.1229 | 0.183126 | tak (slabe/brak) |

## Cliff's delta na delta_cc (AI vs T) per repo

| repo | A_vs_T | G_vs_T | C_vs_T |
|---|---|---|---|
| flask | 0.6286 | 0.56 | 0.5429 |
| httpie | 0.8286 | 0.7917 | 0.8286 |
| requests | 0.7143 | 0.6923 | 0.6571 |

## Mediana pass_ratio per repo x warunek

| repo | T | A | G | C |
|---|---|---|---|---|
| flask | 0.9667 | 0.9648 | 0.9667 | 0.963 |
| httpie | 0.9583 | 0.9583 | 0.9542 | 0.9554 |
| requests | 0.9969 | 0.9969 | 0.9969 | 0.9969 |

## Czy ΔCC w warunku A rozni sie miedzy repo?

Kruskal-Wallis: H=3.241, p=0.197789, sizes=[35, 35, 35].
Repozytoria: ['flask', 'httpie', 'requests'].


## Interpretacja

- Jesli kierunek efektu H2 (delta_cc > 0 dla AI vs T) jest spojny we wszystkich repo - efekt jest **zewnetrznie wazny**.
- Jesli H5 (brak korelacji judge↔testy) replikuje sie w kazdym repo, wynik nie jest artefaktem jednego datasetu.
- Roznice w accept rate i pass_ratio mowia o **trudnosci kazdego kodu** - flask/httpie/requests maja rozne style i pokrycie testowe.

