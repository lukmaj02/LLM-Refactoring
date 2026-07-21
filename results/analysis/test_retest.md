# 5.A3 Test-retest reliability LLM-as-Judge (v1 vs v2)

Spjety zbior: **389** par (sample_id, condition) obecnych jednoczesnie w v1 (Faza 4+4B, T=0.2) i v2 (Faza 4C, T=0.0). Dla kazdego z 5 wymiarow LLM-judge porownujemy ocene v1 z ocena v2 - **idealna reliability oznaczaloby wysoka zgodnosc**.

ICC interpretacja (Koo & Li 2016): <0.50 poor, 0.50-0.75 moderate, 0.75-0.90 good, >=0.90 excellent.

## Per-dimension reliability

| Dim | n_pairs | Spearman rho | p | ICC(2,1) | ICC 95% CI | Kappa (quad) | mean_diff (v2-v1) | LoA |
|---|---|---|---|---|---|---|---|---|
| quality_score | 224 | 0.6163 | 0.0 | 0.4553 (poor) | [0.3439, 0.5523] | 0.4542 | 0.04 | [-4.404, 4.485] |
| solid_score | 224 | 0.727 | 0.0 | 0.6993 (moderate) | [0.6389, 0.7697] | 0.722 | 0.335 | [-2.361, 3.031] |
| dry_score | 224 | 0.3686 | 0.0 | 0.4598 (poor) | [0.3523, 0.5589] | 0.4827 | 0.156 | [-2.564, 2.876] |
| kiss_score | 224 | 0.5433 | 0.0 | 0.4699 (poor) | [0.3612, 0.5659] | 0.482 | 0.112 | [-3.251, 3.474] |
| semantic_score | 224 | 0.3964 | 0.0 | 0.3608 (poor) | [0.2402, 0.4685] | 0.3638 | 0.027 | [-5.709, 5.763] |

## Interpretacja

- **quality_score:** Spearman rho = 0.6163, ICC = 0.4553 (poor). Srednia bezwzgledna roznica miedzy v1 i v2 = 1.138 punktow na skali 0-10.

- **semantic_score:** Spearman rho = 0.3964, ICC = 0.3608 (poor).


**Wniosek dla pracy magisterskiej:** wartosci ICC ponizej 0.75 (moderate/poor) oznaczaja, ze LLM-judge **nie jest reliable nawet wobec siebie samego**. Kazda korelacja uzywajaca quality_score jest osłabiona przez attenuation effect - prawdziwa korelacja moze byc wyzsza, ale szum pomiaru ja maskuje. Roznice miedzy v1 i v2 to w czesci tez wynik niedeterminizmu (T=0.2 vs T=0.0).

