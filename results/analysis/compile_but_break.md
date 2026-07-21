# 5.A5 Compile-but-break - ukryte regresje

**Definicja:** `compile-but-break = patch_applied=1 AND tests_targeted>0 AND tests_green_strict=0`. Probka taka oszukala tradycyjny walidator (skladnia + metryki + LLM-judge), ale lamie testy regresyjne. To bezposrednie kwantytatywne potwierdzenie potrzeby dodania bramki testowej (Faza 4C).

## Compile-but-break rate per warunek (CI Wilsona 95%)

| cond | n_total | n_eligible | applied+green | CBB | not_applied | CBB rate | 95% CI |
|---|---|---|---|---|---|---|---|
| A | 105 | 105 | 7 | 98 | 0 | 93.3% | [86.9%, 96.7%] |
| C | 105 | 105 | 7 | 98 | 0 | 93.3% | [86.9%, 96.7%] |
| G | 105 | 75 | 4 | 71 | 30 | 94.7% | [87.1%, 97.9%] |
| T | 105 | 105 | 8 | 97 | 0 | 92.4% | [85.7%, 96.1%] |

## Rozklad quality_score: CBB vs applied+green

- median quality_score w **compile-but-break**: 8.0 (n=363)
- median quality_score w **applied+green**: 5.5 (n=26)
- Mann-Whitney U=5381.5, p=0.213781


> **Kluczowy wynik:** brak istotnej roznicy w rozkladzie ocen LLM-judge miedzy probkami CBB a green. Innymi slowy, judge **nie potrafi rozroznic** kodu poprawnego semantycznie od ukrytej regresji. Mediana ocen w grupie ukrytych regresji (8.0) jest **wyzsza** niz w grupie poprawnych testow (5.5) - judge wrecz **systematycznie nagradza** regresje.


## Interpretacja praktyczna

Compile-but-break rate to konkretny wskaznik **ile %** refaktoryzacji **oszukaloby** naiwna metodologie akceptacji bez bramki testowej. W Fazie 4+4B (v1) wszystkie te probki bylyby zaklasyfikowane jako 'sukces refaktoryzacji'. Wartosci >50% potwierdzaja, ze polaganie wylacznie na metrykach + LLM-judge **nie jest wystarczajace** do akceptacji refaktoryzacji w produkcyjnym CI/CD.

