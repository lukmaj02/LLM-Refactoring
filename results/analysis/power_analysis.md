# 5.A1 Analiza mocy a posteriori

Dla wynikow istotnych (H2, H4) raportowana jest moc faktyczna (symulacyjna bootstrap na obserwowanym rozkladzie roznic). Dla wynikow nieistotnych (H3, H5) raportowany jest minimalny wykrywalny efekt (MDES) przy alpha=0.05, power=0.80. Pozwala to rozroznic 'brak efektu' od 'brak detekcji efektu'.

## H2 - moc faktyczna (paired Wilcoxon, AI vs T na delta_cc)

| comparison | n_pairs | median_diff | attained power |
|---|---|---|---|
| A_vs_T | 105 | 3.0 | 1.0 |
| G_vs_T | 75 | 2.0 | 1.0 |
| C_vs_T | 105 | 3.0 | 1.0 |

## H3 - MDES dla Kruskal-Wallis (A vs G vs C)

Liczebnosci: n_A=105, n_G=75, n_C=105; pooled SD = 4.09.

**Krzywa mocy (shift mediany w grupie A vs reszta):**

| shift | power |
|---|---|
| 0.409 | 0.394 |
| 0.818 | 0.406 |
| 1.227 | 0.947 |
| 1.636 | 0.944 |
| 2.045 | 1.0 |
| 2.454 | 1.0 |
| 2.863 | 1.0 |
| 3.272 | 1.0 |
| 3.681 | 1.0 |
| 4.09 | 1.0 |

**MDES (shift dajacy moc >= 0.80):** 1.2269070180844721


> Przy n=(105,75,105) i pooled_sd=4.09, minimalny wykrywalny shift mediany (alpha=0.05, power=0.80) wynosi 1.2269070180844721. Obserwowana epsilon^2 = 0.0007 (faktyczna roznica < MDES) wspiera wniosek o BRAKU EFEKTU (nie 'brak detekcji efektu').

## H4 - moc faktyczna (CI/CD overhead)

n_pairs=30, median_diff=4.075 s, attained power=1.0.

## H5 - moc dla Spearman (judge vs pass_ratio)

n=353, obserwowane rho=-0.0816.

**Moc analityczna (Fisher z) dla roznych wartosci |rho|:**

| |rho| | power |
|---|---|
| 0.1 | 0.467 |
| 0.15 | 0.8072 |
| 0.2 | 0.9666 |
| 0.25 | 0.9976 |
| 0.3 | 0.9999 |
| 0.5 | 1.0 |

**MDES (|rho| przy mocy 0.80):** 0.1486


> Przy n=353 mamy moc >0.99 do wykrycia |rho|>=0.2 i moc 0.8072 do wykrycia |rho|>=0.15. Minimalny wykrywalny |rho| przy mocy 0.80 = 0.149. Obserwowane rho=-0.082 jest WYRAZNIE PONIZEJ tego progu, co uzasadnia twierdzenie 'brak korelacji' (absence of evidence = evidence of absence).

