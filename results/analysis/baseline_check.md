# Bezposredni pomiar linii bazowej testow (Etap 7.2)

Probka: 21 migawek (po 7/repo, seed 42);
identyczna selekcja testow i konfiguracja pytest (-x) jak w potoku 4C,
lecz kod NIEZMODYFIKOWANY.

| sample_id | repo | metoda | passed | failed+err (baseline) | failed+err (warunek T) | zgodne? |
|---|---|---|---|---|---|---|
| flask_001 | flask | grep_import | 15 | 1 | 1 | tak  |
| flask_003 | flask | grep_import | 29 | 1 | 1 | tak  |
| flask_006 | flask | grep_import | 29 | 1 | 1 | tak  |
| flask_007 | flask | grep_import | 29 | 1 | 0 | NIE  |
| flask_028 | flask | grep_import | 29 | 1 | 1 | tak  |
| flask_032 | flask | grep_import | 1 | 0 | 0 | tak  |
| flask_035 | flask | grep_import | 15 | 1 | 1 | tak  |
| httpie_002 | httpie | grep_import | 36 | 1 | 0 | NIE  |
| httpie_013 | httpie | grep_import | 32 | 1 | 1 | tak  |
| httpie_015 | httpie | grep_import | 20 | 0 | 0 | tak  |
| httpie_021 | httpie | module_fallback | 19 | 1 | 1 | tak  |
| httpie_023 | httpie | grep_import | 20 | 1 | 1 | tak  |
| httpie_031 | httpie | grep_import | 23 | 1 | 1 | tak  |
| httpie_033 | httpie | grep_import | 1 | 1 | 1 | tak  |
| requests_002 | requests | grep_import | 325 | 1 | 0 | NIE  |
| requests_005 | requests | grep_import | 324 | 1 | 1 | tak  |
| requests_008 | requests | grep_import | 324 | 1 | 1 | tak  |
| requests_016 | requests | grep_import | 15 | 1 | 0 | NIE  |
| requests_018 | requests | grep_import | 324 | 1 | 1 | tak  |
| requests_024 | requests | grep_import | 324 | 1 | 1 | tak  |
| requests_035 | requests | grep_import | 324 | 1 | 1 | tak  |

Zgodnosc baseline vs warunek T: 17/21 migawek.