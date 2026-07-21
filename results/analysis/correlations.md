# 5.4 Korelacje Spearmana (Faza 4C)

Wszystkie obliczenia na zbiorze `experiment_results_v2` z `patch_applied=1`. Spearman dlatego, ze EDA wykazalo brak normalnosci.

## Targetowane pary zmiennych

| para | scope | n | rho | p | sig 0.05 |
|---|---|---|---|---|---|
| **changed_pct__vs__quality_score** | global | 389 | 0.5976 | 0.0 | tak |
| changed_pct__vs__quality_score | cond=A | 105 | 0.1471 | 0.134282 | nie |
| changed_pct__vs__quality_score | cond=C | 105 | 0.6664 | 0.0 | tak |
| changed_pct__vs__quality_score | cond=G | 75 | 0.375 | 0.000917 | tak |
| changed_pct__vs__quality_score | cond=T | 104 | -0.2224 | 0.023235 | tak |
| **cc_before__vs__delta_cc** | global | 390 | 0.6245 | 0.0 | tak |
| cc_before__vs__delta_cc | cond=A | 105 | 0.9341 | 0.0 | tak |
| cc_before__vs__delta_cc | cond=C | 105 | 0.9076 | 0.0 | tak |
| cc_before__vs__delta_cc | cond=G | 75 | 0.9237 | 0.0 | tak |
| cc_before__vs__delta_cc | cond=T | 105 | None | None | nie |
| **cc_before__vs__delta_mi** | global | 390 | -0.3888 | 0.0 | tak |
| cc_before__vs__delta_mi | cond=A | 105 | -0.5846 | 0.0 | tak |
| cc_before__vs__delta_mi | cond=C | 105 | -0.5644 | 0.0 | tak |
| cc_before__vs__delta_mi | cond=G | 75 | -0.2518 | 0.029318 | tak |
| cc_before__vs__delta_mi | cond=T | 105 | 0.0146 | 0.882093 | nie |
| **quality_score__vs__pass_ratio** | global | 353 | -0.0816 | 0.12614 | nie |
| quality_score__vs__pass_ratio | cond=A | 96 | 0.0684 | 0.507928 | nie |
| quality_score__vs__pass_ratio | cond=C | 95 | -0.2261 | 0.027572 | tak |
| quality_score__vs__pass_ratio | cond=G | 66 | 0.0174 | 0.889491 | nie |
| quality_score__vs__pass_ratio | cond=T | 96 | -0.172 | 0.093721 | nie |
| **semantic_score__vs__pass_ratio** | global | 353 | 0.0344 | 0.519694 | nie |
| semantic_score__vs__pass_ratio | cond=A | 96 | 0.164 | 0.110316 | nie |
| semantic_score__vs__pass_ratio | cond=C | 95 | -0.1915 | 0.063082 | nie |
| semantic_score__vs__pass_ratio | cond=G | 66 | 0.0542 | 0.665551 | nie |
| semantic_score__vs__pass_ratio | cond=T | 96 | -0.1343 | 0.1921 | nie |
| **response_time_s__vs__delta_cc** | global | 390 | 0.6501 | 0.0 | tak |
| response_time_s__vs__delta_cc | cond=A | 105 | 0.6807 | 0.0 | tak |
| response_time_s__vs__delta_cc | cond=C | 105 | 0.6255 | 0.0 | tak |
| response_time_s__vs__delta_cc | cond=G | 75 | 0.601 | 0.0 | tak |
| response_time_s__vs__delta_cc | cond=T | 105 | None | None | nie |
| **tokens_in__vs__quality_score** | global | 389 | 0.4479 | 0.0 | tak |
| tokens_in__vs__quality_score | cond=A | 105 | 0.0997 | 0.311446 | nie |
| tokens_in__vs__quality_score | cond=C | 105 | -0.0082 | 0.933907 | nie |
| tokens_in__vs__quality_score | cond=G | 75 | 0.0134 | 0.908885 | nie |
| tokens_in__vs__quality_score | cond=T | 104 | None | None | nie |
| **changed_pct__vs__pass_ratio** | global | 353 | -0.0893 | 0.093994 | nie |
| changed_pct__vs__pass_ratio | cond=A | 96 | -0.0372 | 0.719263 | nie |
| changed_pct__vs__pass_ratio | cond=C | 95 | -0.036 | 0.729077 | nie |
| changed_pct__vs__pass_ratio | cond=G | 66 | -0.195 | 0.116613 | nie |
| changed_pct__vs__pass_ratio | cond=T | 96 | 0.0401 | 0.697912 | nie |

## Interpretacja kluczowych wynikow

- **`quality_score` vs `pass_ratio`**: oczekiwana wysoka korelacja, gdyby LLM-judge poprawnie ocenial semantyke. Wartosc bliska 0 = potwierdzenie tezy pracy.
- **`changed_pct` vs `quality_score`**: czy modele dostaja wyzsze oceny za 'wiekszy' refaktoring? Dodatnia korelacja = ryzyko bias (judge nagradza zmiane, nie poprawe).
- **`cc_before` vs `delta_cc`**: silna dodatnia = regresja ku sredniej, klasyczny efekt; wieksze CC -> wieksza redukcja.
- **`semantic_score` vs `pass_ratio`**: poddyrektywa kluczowego wyniku - czy konkretny wymiar 'Semantic Equivalence' lepiej koreluje z testami niz `quality_score`?

