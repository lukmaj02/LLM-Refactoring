# 5.1 EDA - Statystyki opisowe i test normalnosci

Statystyki obliczone na lacie poprawnych skladniowo refaktoryzacji (`patch_applied=1`). Test Shapiro-Wilka: H0 = rozklad normalny; p > 0,05 nie pozwala odrzucic H0.

## Dane z v1 (Fazy 4 + 4B)

### ΔCC (cc_before − cc_after)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 105 | 4.314 | 3.0 | 4.41 | 7.0 | 0.87 | 0.0 | nie |
| C | 105 | 3.971 | 3.0 | 4.548 | 6.0 | 0.8415 | 0.0 | nie |
| G | 103 | 2.485 | 0.0 | 4.597 | 3.0 | 0.6142 | 0.0 | nie |
| T | 105 | 0.0 | 0.0 | 0.0 | 0.0 | None | None | - |

### ΔMI (mi_after − mi_before)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 105 | -8.674 | -5.95 | 10.279 | 16.07 | 0.9178 | 7e-06 | nie |
| C | 105 | -4.785 | -1.26 | 7.587 | 8.08 | 0.8485 | 0.0 | nie |
| G | 103 | 0.863 | 0.0 | 9.449 | 0.555 | 0.6541 | 0.0 | nie |
| T | 105 | 0.026 | 0.0 | 0.386 | 0.0 | 0.5011 | 0.0 | nie |

### Quality score (LLM-judge, 0–10)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 103 | 7.602 | 9.0 | 2.311 | 2.0 | 0.6958 | 0.0 | nie |
| C | 84 | 8.31 | 9.0 | 1.299 | 1.0 | 0.7571 | 0.0 | nie |
| G | 51 | 7.0 | 8.0 | 2.835 | 2.5 | 0.7462 | 0.0 | nie |

### Changed pct

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 70 | 1.366 | 1.371 | 0.274 | 0.374 | 0.989 | 0.804493 | tak |
| C | 67 | 1.387 | 1.405 | 0.337 | 0.507 | 0.9667 | 0.069629 | tak |
| G | 65 | 1.318 | 1.227 | 0.368 | 0.615 | 0.9311 | 0.001356 | nie |
| T | 2 | 0.929 | 0.929 | 0.101 | 0.071 | None | None | - |


## Dane z v2 (Faza 4C)

### ΔCC (cc_before − cc_after)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 105 | 4.152 | 3.0 | 4.09 | 6.0 | 0.8811 | 0.0 | nie |
| C | 105 | 3.695 | 3.0 | 4.107 | 6.0 | 0.8473 | 0.0 | nie |
| G | 75 | 3.427 | 2.0 | 4.107 | 5.0 | 0.8072 | 0.0 | nie |
| T | 105 | 0.0 | 0.0 | 0.0 | 0.0 | None | None | - |

### ΔMI (mi_after − mi_before)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 105 | -8.648 | -4.95 | 10.323 | 16.09 | 0.9064 | 2e-06 | nie |
| C | 105 | -4.697 | -1.58 | 7.613 | 7.83 | 0.8232 | 0.0 | nie |
| G | 75 | 1.352 | 0.0 | 9.875 | 3.445 | 0.7298 | 0.0 | nie |
| T | 105 | 0.026 | 0.0 | 0.386 | 0.0 | 0.5011 | 0.0 | nie |

### Quality score (LLM-judge, 0–10)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 105 | 7.41 | 9.0 | 2.571 | 2.0 | 0.6989 | 0.0 | nie |
| C | 105 | 7.619 | 8.0 | 1.948 | 3.0 | 0.8301 | 0.0 | nie |
| G | 75 | 7.147 | 8.0 | 2.481 | 4.0 | 0.8299 | 0.0 | nie |
| T | 104 | 4.587 | 5.0 | 1.391 | 0.0 | 0.3357 | 0.0 | nie |

### Changed pct

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 105 | 0.541 | 0.545 | 0.207 | 0.335 | 0.9784 | 0.083495 | tak |
| C | 105 | 0.434 | 0.487 | 0.275 | 0.452 | 0.9341 | 5.7e-05 | nie |
| G | 75 | 0.494 | 0.558 | 0.315 | 0.449 | 0.9209 | 0.000173 | nie |
| T | 105 | 0.027 | 0.0 | 0.05 | 0.039 | 0.6136 | 0.0 | nie |

### Pass ratio (testy)

| condition | n | mean | median | std | IQR | Shapiro W | Shapiro p | Normal? |
|---|---|---|---|---|---|---|---|---|
| A | 96 | 0.92 | 0.967 | 0.183 | 0.059 | 0.3934 | 0.0 | nie |
| C | 95 | 0.893 | 0.967 | 0.231 | 0.059 | 0.4543 | 0.0 | nie |
| G | 66 | 0.931 | 0.967 | 0.14 | 0.059 | 0.432 | 0.0 | nie |
| T | 96 | 0.938 | 0.967 | 0.151 | 0.059 | 0.3463 | 0.0 | nie |
