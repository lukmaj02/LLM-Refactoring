# Test-retest sedziego LLM na identycznych artefaktach (Etap 2.1)

n = 150 par (sample_id x warunek); przebieg 1 = eksperyment glowny 4C,
przebieg 2 = ponowna ocena TYCH SAMYCH plikow kodu (skrypt run_judge_retest.py,
sedzia: Gemini 2.5 Flash, T=0,0).

| Wymiar | ICC(2,1) | 95% CI (bootstrap) | interpretacja | kappa_w | sr. |roznica| | LoA +/- |
|---|---|---|---|---|---|---|
| quality_score | 0.777 | [0.66; 0.88] | dobra (good) | 0.775 | 0.75 | 3.15 |
| semantic_score | 0.671 | [0.38; 0.87] | umiarkowana (moderate) | 0.669 | 0.51 | 3.88 |
| solid_score | 0.913 | [0.87; 0.95] | doskonala (excellent) | 0.913 | 0.35 | 1.45 |
| dry_score | 0.444 | [0.04; 0.75] | slaba (poor) | 0.442 | 0.53 | 2.45 |
| kiss_score | 0.730 | [0.60; 0.85] | umiarkowana (moderate) | 0.728 | 0.69 | 2.64 |

Bland-Altman (quality_score): srednia roznica = -0.15, granice zgodnosci [-3.30; 3.00] na skali 0-10.

Zgodnosc idealna (identyczna ocena quality): 61.3% par; roznica >= 2 pkt: 12.0%.
