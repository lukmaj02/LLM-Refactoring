# 5.2 Testy hipotez

Wszystkie testy nieparametryczne (rozklady nie sa normalne, p<0,05 w Shapiro-Wilka, sekcja 5.1). Poziom istotnosci alpha=0,05. Korekta Bonferroniego stosowana przy testach post-hoc.

## H1 - Semantic equivalence (semantic_score vs 8)

H0: median(semantic_score) >= 8 (model osiaga prog wysokiej rownowaznosci). H1: median < 8. Wilcoxon one-sample, `alternative='less'`. Odrzucenie H0 = model NIE osiaga progu.

| condition | n | median | stat | p | p_fdr | reject H0? |
|---|---|---|---|---|---|---|
| A | 105 | 10.0 | 4463.5 | 1.0 | 1.0 | nie |
| C | 105 | 10.0 | 5356.0 | 1.0 | 1.0 | nie |
| G | 75 | 10.0 | 2277.0 | 1.0 | 1.0 | nie |
| T | 104 | 10.0 | 5356.0 | 1.0 | 1.0 | nie |

## H2 - AI vs traditional (ΔCC)

Paired Wilcoxon na delta_cc dla tych samych probek (model AI vs T).

| comparison | n_pairs | median_diff | stat | p | p_fdr | r | reject H0? |
|---|---|---|---|---|---|---|---|
| A_vs_T | 105 | 3.0 | 0.0 | 0.0 | 0.0 | 0.868 | tak |
| G_vs_T | 75 | 2.0 | 0.0 | 0.0 | 0.0 | 0.869 | tak |
| C_vs_T | 105 | 3.0 | 5.0 | 0.0 | 0.0 | 0.867 | tak |

## H3 - Roznice miedzy modelami AI (A, G, C) na ΔCC

**Kruskal-Wallis:** H=2.19, p=0.334538, p_fdr=0.566141, epsilon^2=0.0007, n=285, k=3.

Post-hoc: dunn-bonferroni (scikit-posthocs) (Dunn 1964 z rangami z polaczonej proby, korekta Bonferroniego):

| pair | n_a | n_b | p_bonferroni | p_fdr | sig FDR 0.05? |
|---|---|---|---|---|---|
| A vs C | 105 | 105 | 0.942642 | 1.0 | nie |
| A vs G | 105 | 75 | 0.462722 | 0.727135 | nie |
| C vs G | 105 | 75 | 1.0 | 1.0 | nie |

## H4 - Narzut CI/CD (baseline vs arp)

Median baseline: 0.82 s, median ARP: 4.89 s, median overhead: 4.07 s (30 commitow).

Wilcoxon paired: n_pairs=30, median_diff=4.075, p=0.0, r=0.873, reject H0=tak.

## H5 - LLM-judge vs faktyczne testy (KLUCZOWY WYNIK)

**Spearman (overall):** rho=-0.082, p=0.12614, n=353.
Wartosc bliska 0 wspiera teze: LLM-judge ocenia kod **nieskorelowanie** z faktycznym pass rate testow.

Per warunek:

| condition | n | rho | p |
|---|---|---|---|
| A | 96 | 0.068 | 0.507928 |
| C | 95 | -0.226 | 0.027572 |
| G | 66 | 0.017 | 0.889491 |
| T | 96 | -0.172 | 0.093721 |

**Mann-Whitney (quality_score: testy zielone vs nie):** n_green=26, n_notgreen=327, median_green=5.5, median_notgreen=8.0, p=0.20334.
Brak istotnej roznicy = LLM-judge nie potrafi rozroznic semantycznie poprawnych od bledynych refaktoryzacji.

## H6 - Accept rate v1 (Faza 4+4B) vs v2 (Faza 4C)

Test Fishera 2x2 (accepted/rejected w v1 vs v2). Spodziewamy drastycznej roznicy bo v2 dodalo bramke testowa.

| cond | a1 | r1 | a2 | r2 | OR | p | p_fdr | sig FDR? |
|---|---|---|---|---|---|---|---|---|
| A | 81 | 24 | 5 | 100 | 67.5 | 0.0 | 0.0 | tak |
| G | 46 | 59 | 2 | 73 | 28.458 | 0.0 | 0.0 | tak |
| C | 70 | 35 | 4 | 101 | 50.5 | 0.0 | 0.0 | tak |
| T | 13 | 92 | 0 | 105 | inf | 0.000164 | 0.000451 | tak |

## Korekta multiple-testing (Benjamini-Hochberg FDR)

Liczba testow w rodzinie: 22. Metoda: `Benjamini-Hochberg FDR (statsmodels.fdr_bh)`. Alpha = 0.05.

| test | p_raw | p_fdr | sig FDR 0.05? |
|---|---|---|---|
| H1[A] | 1.0 | 1.0 | nie |
| H1[C] | 1.0 | 1.0 | nie |
| H1[G] | 1.0 | 1.0 | nie |
| H1[T] | 1.0 | 1.0 | nie |
| H2[A_vs_T] | 0.0 | 0.0 | tak |
| H2[G_vs_T] | 0.0 | 0.0 | tak |
| H2[C_vs_T] | 0.0 | 0.0 | tak |
| H3[kruskal] | 0.334538 | 0.566141 | nie |
| H3[Dunn:A vs C] | 0.942642 | 1.0 | nie |
| H3[Dunn:A vs G] | 0.462722 | 0.727135 | nie |
| H3[Dunn:C vs G] | 1.0 | 1.0 | nie |
| H4[wilcoxon] | 0.0 | 0.0 | tak |
| H5[spearman_overall] | 0.12614 | 0.25228 | nie |
| H5[spearman_A] | 0.507928 | 0.744961 | nie |
| H5[spearman_C] | 0.027572 | 0.067398 | nie |
| H5[spearman_G] | 0.889491 | 1.0 | nie |
| H5[spearman_T] | 0.093721 | 0.206186 | nie |
| H5[MW_green_vs_notgreen] | 0.20334 | 0.37279 | nie |
| H6[A] | 0.0 | 0.0 | tak |
| H6[G] | 0.0 | 0.0 | tak |
| H6[C] | 0.0 | 0.0 | tak |
| H6[T] | 0.000164 | 0.000451 | tak |

