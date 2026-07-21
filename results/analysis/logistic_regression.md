# 5.A2 Regresja logistyczna: tests_green ~ predyktory

Cel: czy `quality_score` (LLM-judge) wnosi inkrementalna wartosc predykcyjna dla `tests_green_strict` PO kontroli na rozmiar zmiany (`changed_pct`), zlozonosc poczatkowa (`cc_before`) i warunek eksperymentu? To multivariate fortyfikacja H5.

## Porownanie modeli (information criteria)

| Model | Predyktory | n | LogLik | AIC | BIC | McFadden R² | LR p |
|---|---|---|---|---|---|---|---|
| Model_1_main | y ~ quality_score + changed_pct + cc_before + C(condition) | 389 | -89.05 | 192.1 | 219.845 | 0.0671 | 0.0462 |
| Model_2_semantic | y ~ semantic_score + changed_pct + cc_before + C(condition) | 389 | -88.778 | 191.556 | 219.301 | 0.0699 | 0.03779 |
| Model_3_baseline | y ~ changed_pct + cc_before + C(condition) | 389 | -89.075 | 190.149 | 213.931 | 0.0668 | 0.025756 |

## Walidacja krzyzowa (5-fold stratified)

| Model | ROC AUC mean | AUC SD | Accuracy mean | Brier score |
|---|---|---|---|---|
| Model_1_main | 0.6494 | 0.0965 | 0.9332 | 0.0635 |
| Model_2_semantic | 0.6385 | 0.0934 | 0.9332 | 0.0634 |
| Model_3_baseline | 0.6438 | 0.1023 | 0.9332 | 0.0633 |

## Model_1_main - szczegoly

| zmienna | coef | SE | z | p | OR | 95% CI |
|---|---|---|---|---|---|---|
| Intercept | -2.146 | 0.8383 | -2.56 | 0.010468 | 0.117 | [0.0226, 0.6047] |
| C(condition)[T.C] | 0.26 | 0.5945 | 0.437 | 0.661908 | 1.2969 | [0.4044, 4.1586] |
| C(condition)[T.G] | -0.1932 | 0.6642 | -0.291 | 0.771118 | 0.8243 | [0.2242, 3.0303] |
| C(condition)[T.T] | 0.8126 | 0.772 | 1.053 | 0.292566 | 2.2537 | [0.4963, 10.2338] |
| quality_score | -0.0232 | 0.1036 | -0.224 | 0.822432 | 0.977 | [0.7975, 1.1969] |
| changed_pct | 1.3642 | 0.9681 | 1.409 | 0.158782 | 3.9124 | [0.5867, 26.0888] |
| cc_before | -0.1642 | 0.0565 | -2.903 | 0.003693 | 0.8486 | [0.7596, 0.9481] |

## Model_2_semantic - szczegoly

| zmienna | coef | SE | z | p | OR | 95% CI |
|---|---|---|---|---|---|---|
| Intercept | -3.1805 | 1.4833 | -2.144 | 0.032022 | 0.0416 | [0.0023, 0.761] |
| C(condition)[T.C] | 0.2219 | 0.5921 | 0.375 | 0.707898 | 1.2484 | [0.3911, 3.9846] |
| C(condition)[T.G] | -0.2128 | 0.6631 | -0.321 | 0.748261 | 0.8083 | [0.2204, 2.9647] |
| C(condition)[T.T] | 0.8579 | 0.7608 | 1.128 | 0.259497 | 2.3582 | [0.5308, 10.4757] |
| semantic_score | 0.0928 | 0.1348 | 0.688 | 0.491257 | 1.0972 | [0.8425, 1.4291] |
| changed_pct | 1.4679 | 0.9852 | 1.49 | 0.136252 | 4.3399 | [0.6293, 29.9287] |
| cc_before | -0.1711 | 0.0551 | -3.108 | 0.001883 | 0.8427 | [0.7565, 0.9387] |

## Model_3_baseline - szczegoly

| zmienna | coef | SE | z | p | OR | 95% CI |
|---|---|---|---|---|---|---|
| Intercept | -2.2683 | 0.6399 | -3.545 | 0.000393 | 0.1035 | [0.0295, 0.3627] |
| C(condition)[T.C] | 0.2486 | 0.5905 | 0.421 | 0.673788 | 1.2822 | [0.403, 4.0796] |
| C(condition)[T.G] | -0.2017 | 0.6621 | -0.305 | 0.760656 | 0.8173 | [0.2233, 2.9922] |
| C(condition)[T.T] | 0.846 | 0.7571 | 1.117 | 0.26385 | 2.3303 | [0.5284, 10.2774] |
| changed_pct | 1.3412 | 0.9675 | 1.386 | 0.165651 | 3.8238 | [0.5741, 25.4698] |
| cc_before | -0.168 | 0.0544 | -3.088 | 0.002012 | 0.8454 | [0.7599, 0.9405] |

## Interpretacja

- Roznica AIC Model_1 (z quality_score) vs Model_3 (baseline): +1.95. Konwencja Burnham & Anderson: roznica > 2 = istotna; < 2 = modele rownowazne.

- Wspolczynnik `quality_score` w Model_1: coef=-0.0232, p=0.822432, OR=0.977 (CI [0.7975, 1.1969]).

- Jesli OR(quality_score) ~ 1.0 i p > 0.05, to **LLM-judge nie wnosi informacji predykcyjnej po kontroli na rozmiar zmiany** - potwierdzenie H5 na poziomie multivariate.

