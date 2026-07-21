# Liczby rozdziału 4 — jedyne źródło prawdy (faza 4C)

Wygenerowano skryptem `scripts/analysis/thesis_numbers.py`; n = 420 obserwacji.

## 1. Przepływ przez bramki (tab:wyniki-kaskada)

| Pozycja | T | A | G | C |
|---|---|---|---|---|
| Wejście | 105 | 105 | 105 | 105 |
| po B1 (składnia) | 105 | 105 | 75 | 105 |
| po B2 (niepusta zmiana) | 105 | 105 | 75 | 105 |
| po B3 (metryki) | 97 | 103 | 73 | 102 |
| po B4 (testy) = akceptacja | 0 | 5 | 2 | 4 |

Odsetek akceptacji (z 95% CI Wilsona):

* T: 0/105 = 0.0% (CI 0.0–3.5)
* A: 5/105 = 4.8% (CI 2.1–10.7)
* G: 2/105 = 1.9% (CI 0.5–6.7)
* C: 4/105 = 3.8% (CI 1.5–9.4)
* A+G+C łącznie: 11/315 = 3.49% (CI 2.0–6.1)

## 2. Compile-but-break (tab:wyniki-cbb)

CBB = test_failure / (obserwacje, które przeszły B1–B3).

* T: 97/97 = 100.0% (CI 96.2–100.0)
* A: 98/103 = 95.1% (CI 89.1–97.9)
* G: 71/73 = 97.3% (CI 90.5–99.2)
* C: 98/102 = 96.1% (CI 90.3–98.5)

### CBB wg repozytorium (tylko A/G/C)

* flask: 86/88 = 97.7% (CI 92.1–99.4)
* httpie: 85/94 = 90.4% (CI 82.8–94.9)
* requests: 96/96 = 100.0% (CI 96.2–100.0)
* test niezależności repo×CBB: chi2 = 12.42, p = 0.002

### CBB wg warstwy CC (tylko A/G/C)

* CC 5-6: 114/120 = 95.0% (CI 89.5–97.7)
* CC 7-9: 32/34 = 94.1% (CI 80.9–98.4)
* CC >=10: 121/124 = 97.6% (CI 93.1–99.2)
* test niezależności warstwa×CBB: chi2 = 1.45, p = 0.485

## 3. Kryterium surowe vs złagodzone (sygnał linii bazowej testów)

`green_relaxed` dopuszcza dokładnie 1 oblany test (podejrzenie testu
failującego bazowo w środowisku — do weryfikacji w Etapie 1.3).

| Warunek | akceptacja strict | akceptacja relaxed (failed<=1) |
|---|---|---|
| T | 0/97 | 86/97 |
| A | 5/103 | 91/103 |
| G | 2/73 | 63/73 |
| C | 4/102 | 87/102 |

Obserwacje odrzucone przez B4 z DOKŁADNIE 1 oblanym testem: 325 z 364 wszystkich test_failure.

## 4. Statystyki opisowe (tab:wyniki-eda-deskryptywka)

| Zmienna | T | A | G | C |
|---|---|---|---|---|
| ΔCC (po-przed) | 0.00 (IQR 0.00) | -3.00 (IQR 6.00) | -2.00 (IQR 5.00) | -3.00 (IQR 6.00) |
| ΔMI | 0.00 (IQR 0.00) | -4.95 (IQR 16.09) | 0.00 (IQR 3.44) | -1.58 (IQR 7.83) |
| pass_ratio | 0.97 (IQR 0.06) | 0.97 (IQR 0.06) | 0.97 (IQR 0.06) | 0.97 (IQR 0.06) |
| quality_score | 5.00 (IQR 0.00) | 9.00 (IQR 2.00) | 8.00 (IQR 4.00) | 8.00 (IQR 3.00) |
| semantic_score | 10.00 (IQR 0.00) | 10.00 (IQR 0.00) | 10.00 (IQR 0.00) | 10.00 (IQR 0.00) |

ΔCC (A+G+C, n=285): średnia = -3.79, mediana = -3.0, SD = 4.10
95% CI (bootstrap, percentyle) średniej ΔCC: [-4.32; -3.33]

## 5. Normalność (Shapiro–Wilk)

* d_cc: W = 0.853, p = 8.80e-16, n = 285
* d_mi: W = 0.868, p = 6.53e-15, n = 285
* pass_ratio: W = 0.418, p = 4.99e-28, n = 257
* quality_score: W = 0.787, p = 5.60e-19, n = 285

## 6. PB1: Wilcoxon (H: ΔCC < 0)

* A: W = 0, z = -7.59, p = 1.65e-14, r = -0.87, n = 76
* G: W = 0, z = -6.23, p = 2.38e-10, r = -0.87, n = 51
* C: W = 5, z = -7.41, p = 6.40e-14, r = -0.87, n = 73
* A+G+C: W = 12, z = -12.27, p = 6.84e-35, r = -0.87, n = 200

## 7. PB2: porównanie modeli

* Kruskal–Wallis (ΔCC, grupy A/G/C): H = 2.19, p = 0.335, epsilon^2 = 0.001, n = 285
* Friedman (ΔCC, pary kompletne): chi2 = 9.89, p = 0.007, n = 75
* Parowane Wilcoxony (ΔCC):
  * A vs G: p = 0.413, p_FDR = 0.413, n = 42
  * A vs C: p = 0.009, p_FDR = 0.026, n = 54
  * G vs C: p = 0.062, p_FDR = 0.094, n = 34
* Cochran Q (akceptacja, pary): Q = 2.80, p = 0.247, n = 105
* chi2 niezależności akceptacja×model (odpowiednik Fishera): chi2 = 1.32, p = 0.517

## 8. PB3: sędzia vs testy

* Spearman rho = -0.047, p = 0.451, n = 257 (A/G/C)
* Pearson r = -0.015, p = 0.813 (dla porównania)
* Spearman z warunkiem T: rho = -0.082, p = 0.126, n = 353

## 9. PB4: regresja logistyczna (tests_green_strict)

| Predyktor | OR | 95% CI | p |
|---|---|---|---|
| C(condition)[T.C] | 1.095 | [0.348; 3.444] | 0.876 |
| C(condition)[T.G] | 0.752 | [0.206; 2.752] | 0.667 |
| quality_score | 1.056 | [0.824; 1.353] | 0.669 |
| d_cc | 1.361 | [1.057; 1.751] | 0.017 |
| changed_pct | 3.479 | [0.446; 27.106] | 0.234 |

AUC = 0.691 (0,5 = klasyfikator losowy); n = 285, zdarzenia = 18

## 10. Koszty i czasy (Etap 1.6)

| Warunek | mediana tokens_out | mediana czasu [s] | suma kosztu [USD] |
|---|---|---|---|
| A | 239 | 3.8 | 1.92 |
| G | 233 | 14.1 | 0.13 |
| C | 356 | 5.8 | 3.06 |

## 11. Zgodność między modelami (CBB na tych samych migawkach)

* Jaccard CBB A∩G: 70/99 = 0.71
* Jaccard CBB A∩C: 98/98 = 1.00
* Jaccard CBB G∩C: 70/99 = 0.71
* migawki z CBB we wszystkich trzech modelach: 70/105

## 12. CBB skorygowane o linię bazową (Etap 1.3a)

Warunek T (sam autopep8/autoflake) nie zmienia zachowania programu, więc
jego wynik testów na danej migawce traktujemy jako linię bazową środowiska.
Regresja przypisywalna refaktoryzacji = model obla WIĘCEJ testów niż T
na tej samej migawce (failures+errors).

| Warunek | n par z T | regresja > baseline | CBB skorygowane | CI Wilsona |
|---|---|---|---|---|
| A | 97 | 0 | 0.0% | [0.0; 3.8] |
| G | 70 | 0 | 0.0% | [0.0; 5.2] |
| C | 97 | 0 | 0.0% | [0.0; 3.8] |

Kontrola spójności doboru testów (liczba plików testowych rożna niż w T): {'A': 0, 'G': 30, 'C': 0}

Akceptacja skorygowana (przeszło B1–B3 i nie obla więcej testów niż T,
w mianowniku pełne n=105 na warunek):

* A: 97/105 = 92.4% (CI 85.7–96.1)
* G: 70/105 = 66.7% (CI 57.2–75.0)
* C: 97/105 = 92.4% (CI 85.7–96.1)

Uwaga interpretacyjna: korekta zakłada, że T i model dostały ten sam
zestaw testów (kontrola powyżej) oraz że zmiany T są semantycznie
neutralne (autopep8 formatuje; autoflake usuwa nieużywane importy —
ryzyko naruszenia importów z efektem ubocznym omówić w ograniczeniach).

## 13. Zaakceptowane refaktoryzacje (Etap 1.4)

| sample_id | warunek | repo | CC przed→po | MI przed→po | quality |
|---|---|---|---|---|---|
| flask_014 | A | flask | 7→7 | 67.3→68.0 | 7.0 |
| httpie_015 | A | httpie | 10→4 | 71.7→63.8 | 9.0 |
| httpie_026 | A | httpie | 6→3 | 86.9→76.6 | 9.0 |
| httpie_027 | A | httpie | 5→3 | 87.6→82.8 | 9.0 |
| httpie_034 | A | httpie | 4→4 | 74.2→78.9 | 8.0 |
| httpie_015 | C | httpie | 10→5 | 71.7→63.9 | 9.0 |
| httpie_026 | C | httpie | 6→5 | 86.9→88.4 | 8.0 |
| httpie_027 | C | httpie | 5→3 | 87.6→87.5 | 7.0 |
| httpie_034 | C | httpie | 4→2 | 74.2→81.9 | 4.0 |
| flask_017 | G | flask | 7→4 | 86.7→86.3 | 9.0 |
| httpie_015 | G | httpie | 10→4 | 71.7→63.4 | 10.0 |
