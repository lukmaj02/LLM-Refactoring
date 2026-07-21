# 5.3 Wielkosci efektow i bootstrap 95% CI dla median

Bootstrap BCa (B=10 000, scipy.stats.bootstrap). Cliff's delta kategoryzowany wg Romano et al. 2006: |d|<0.147 znikomy, <0.33 maly, <0.474 sredni, >=0.474 duzy.

## Bootstrap 95% CI dla median - delta_cc

| condition | n | median | CI low | CI high | method |
|---|---|---|---|---|---|
| A | 105 | 3.0 | 2.0 | 5.0 | percentile |
| C | 105 | 3.0 | 2.0 | 4.0 | percentile |
| G | 75 | 2.0 | 1.0 | 3.0 | percentile |
| T | 105 | 0.0 | 0.0 | 0.0 | percentile |

## Bootstrap 95% CI dla median - delta_mi

| condition | n | median | CI low | CI high | method |
|---|---|---|---|---|---|
| A | 105 | -4.95 | -9.12 | -2.96 | BCa |
| C | 105 | -1.58 | -3.01 | -0.63 | BCa |
| G | 75 | 0.0 | -0.59 | 0.0 | percentile |
| T | 105 | 0.0 | 0.0 | 0.0 | percentile |

## Bootstrap 95% CI dla median - quality_score

| condition | n | median | CI low | CI high | method |
|---|---|---|---|---|---|
| A | 105 | 9.0 | 8.0 | 9.0 | percentile |
| C | 105 | 8.0 | 7.0 | 9.0 | BCa |
| G | 75 | 8.0 | 8.0 | 9.0 | percentile |
| T | 104 | 5.0 | 5.0 | 5.0 | percentile |

## Bootstrap 95% CI dla median - pass_ratio

| condition | n | median | CI low | CI high | method |
|---|---|---|---|---|---|
| A | 96 | 0.967 | 0.958 | 0.97 | percentile |
| C | 95 | 0.967 | 0.958 | 0.974 | BCa |
| G | 66 | 0.967 | 0.958 | 0.987 | BCa |
| T | 96 | 0.967 | 0.958 | 0.973 | percentile |

## Cliff's delta vs T - delta_cc

| comparison | n_a | n_b | Cliff d | A12 | magnitude |
|---|---|---|---|---|---|
| A_vs_T | 105 | 105 | 0.7238 | 0.8619 | large |
| C_vs_T | 105 | 105 | 0.6762 | 0.8381 | large |
| G_vs_T | 75 | 105 | 0.68 | 0.84 | large |

## Cliff's delta vs T - delta_mi

| comparison | n_a | n_b | Cliff d | A12 | magnitude |
|---|---|---|---|---|---|
| A_vs_T | 105 | 105 | -0.5871 | 0.2064 | large |
| C_vs_T | 105 | 105 | -0.5079 | 0.246 | large |
| G_vs_T | 75 | 105 | -0.1453 | 0.4274 | negligible |

## Cliff's delta vs T - quality_score

| comparison | n_a | n_b | Cliff d | A12 | magnitude |
|---|---|---|---|---|---|
| A_vs_T | 105 | 104 | 0.6768 | 0.8384 | large |
| C_vs_T | 105 | 104 | 0.7535 | 0.8767 | large |
| G_vs_T | 75 | 104 | 0.6308 | 0.8154 | large |

## Cliff's delta vs T - pass_ratio

| comparison | n_a | n_b | Cliff d | A12 | magnitude |
|---|---|---|---|---|---|
| A_vs_T | 96 | 96 | -0.0711 | 0.4645 | negligible |
| C_vs_T | 95 | 96 | -0.0891 | 0.4554 | negligible |
| G_vs_T | 66 | 96 | -0.0949 | 0.4526 | negligible |

