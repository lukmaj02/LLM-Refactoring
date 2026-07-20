# Automatyczny Refactoring z użyciem LLM — kod źródłowy pracy

Kod eksperymentu porównującego jakość automatycznego refactoringu funkcji w Pythonie
przy pomocy dużych modeli językowych (LLM) względem podejścia tradycyjnego.

Eksperyment działa na trzech repozytoriach open-source (`requests`, `flask`, `httpie`)
i porównuje pięć warunków:

| Warunek | Opis |
|---------|------|
| `K` | Kontrola (kod bez zmian) |
| `T` | Refactoring tradycyjny (`autopep8` / `autoflake`) |
| `A` | LLM — OpenAI (`gpt-4o`) |
| `G` | LLM — Google Gemini (`gemini-2.5-flash`) |
| `C` | LLM — Anthropic Claude (`claude-sonnet`) |

Dla każdej próbki mierzone są metryki (CC, MI, LOC), wyniki testów `pytest`
oraz ocena jakości przez „LLM-as-Judge”. Wyniki zapisywane są do bazy SQLite.

---

## Szybki start (jeden skrypt)

Cały pipeline (inicjalizacja bazy → dane → przebieg → analiza) uruchamia
orchestrator `run_all.py`. Wykonaj najpierw kroki 1–2 (instalacja i `.env`)
oraz przygotuj repozytoria (patrz sekcja 4), a potem:

```powershell
python run_all.py                 # pełny pipeline
python run_all.py --list          # pokaż wszystkie kroki
python run_all.py --dry-run       # pokaż plan i gotowość (bez uruchamiania)
python run_all.py --skip-analysis # bez fazy analizy
python run_all.py --limit 5 --conditions T A   # przekazane do run_single_pass
python run_all.py --start-at sample_functions --stop-after measure_baseline
```

`run_all.py` sprawdza prerekwizyty każdego kroku (sklonowane repo, zrzuty radona,
snapshoty, venvy, klucze API) i zatrzymuje się z czytelnym komunikatem, jeśli
czegoś brakuje. Kroki analizy są niekrytyczne — ich błąd nie przerywa pipeline.
Poszczególne kroki można też uruchamiać ręcznie (sekcje 3–6 poniżej).

---

## Wymagania

- Python 3.10+ (kod używa składni `int | float`, `str | None`)
- `git` (do klonowania badanych repozytoriów)
- Klucze API do modeli, których chcesz użyć: OpenAI, Google Gemini, Anthropic

## 1. Instalacja

```powershell
# (opcjonalnie) wirtualne środowisko
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# zależności
pip install -r requirements.txt
```

## 2. Konfiguracja (`.env`)

Utwórz plik `.env` w katalogu głównym projektu. Wczytywany jest automatycznie
przez `src/config.py`. Ustaw tylko klucze modeli, których używasz.

```env
# Klucze API
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...

# Parametry eksperymentu (opcjonalne — poniżej wartości domyślne)
RANDOM_SEED=42
SAMPLE_PER_REPO=35
MIN_CC_THRESHOLD=5
MAX_API_COST_USD=20.0

# Ścieżki (opcjonalne)
DATA_DIR=data
RESULTS_DIR=results
LOGS_DIR=logs
DB_PATH=results/results.db

# Nazwy modeli (opcjonalne — nadpisują domyślne)
MODEL_OPENAI=gpt-4o-2024-08-06
MODEL_GEMINI=gemini-2.5-flash
MODEL_ANTHROPIC=claude-sonnet-4-6
```

> Uwaga: klucze API i baza wyników nie powinny trafiać do repozytorium.
> Trzymaj `.env` i katalog `results/` poza kontrolą wersji.

## 3. Inicjalizacja bazy danych

```powershell
python scripts\init_db.py       # tabele bazowe (Fazy 4 / 4B)
python scripts\init_db_v2.py    # tabela experiment_results_v2 (Faza 4C, single-pass)
```

## 4. Przygotowanie danych badanych repozytoriów

Najpierw sklonuj badane repozytoria do `data/repos/` (`requests`, `flask`,
`httpie`) i wygeneruj surowe zrzuty radona (wymagane przez losowanie próbek):

```powershell
radon cc data/repos/requests -s --json > data/results/requests_cc_raw.json
radon mi data/repos/requests --json > data/results/requests_mi_raw.json
# analogicznie dla flask i httpie
```

Następnie, w tej kolejności (kolejność jest istotna — kolejne kroki czytają
wyniki poprzednich):

```powershell
# 1) wylosuj próbki funkcji (deterministycznie, wg RANDOM_SEED)
python scripts\sample_functions.py     # -> data/samples/functions_sample.json

# 2) wytnij snapshoty wylosowanych funkcji
python scripts\extract_snapshots.py    # -> data/snapshots/*.py + index.json

# 3) zmierz metryki bazowe (warunek K); czyta data/snapshots/index.json
python scripts\measure_baseline.py

# 4) zbuduj izolowane venvy dla każdego repo (potrzebne do uruchamiania testów)
python scripts\setup_repo_venvs.py
```

## 5. Uruchomienie eksperymentu (Faza 4C — single-pass)

Główny orchestrator generuje refactoring, uruchamia testy celowane i ocenę jakości,
a wyniki zapisuje do `experiment_results_v2`.

```powershell
# pełny przebieg dla wszystkich warunków
python scripts\run_single_pass.py

# przydatne opcje:
python scripts\run_single_pass.py --conditions T A          # tylko wybrane warunki
python scripts\run_single_pass.py --limit 5                 # ogranicz liczbę próbek
python scripts\run_single_pass.py --samples <sample_id> ... # wybrane próbki
python scripts\run_single_pass.py --no-skip                 # policz ponownie istniejące
python scripts\run_single_pass.py --verbose                 # więcej logów
```

Szybki test poprawności konfiguracji przed pełnym przebiegiem:

```powershell
python scripts\smoke_test.py
```

## 6. Analiza wyników

Skrypty analityczne (statystyki, testy hipotez, wykresy do pracy) znajdują się
w `scripts/analysis/`:

```powershell
python scripts\analysis\eda.py
python scripts\analysis\hypothesis_tests.py
python scripts\analysis\effect_sizes.py
python scripts\analysis\thesis_figures.py
```

---

## Struktura projektu

```
src/                     # rdzeń: pipeline, klient LLM, walidacja, metryki
  config.py              # konfiguracja z .env
  ai_client.py           # klient OpenAI / Gemini / Anthropic
  arp_pipeline.py        # pipeline refactoringu
  prompts.py             # prompty dla modeli
  patch_generator.py     # generowanie i walidacja patchy
  repo_patcher.py        # wstawianie zmian do kopii repo
  test_selector.py       # dobór testów celowanych
  validator.py           # metryki (CC/MI/LOC) i walidacja testami
  quality_validator.py   # LLM-as-Judge
  audit_logger.py        # log audytowy przebiegów

scripts/                 # skrypty uruchomieniowe i pomocnicze
  init_db.py, init_db_v2.py
  measure_baseline.py, sample_functions.py, extract_snapshots.py
  setup_repo_venvs.py
  run_single_pass.py     # główny orchestrator (Faza 4C)
  analysis/              # analiza statystyczna i wykresy

data/                    # repozytoria, snapshoty, venvy, kod po refactoringu
results/                 # baza SQLite z wynikami
logs/                    # logi przebiegów
```

## Typowy przepływ (skrót)

```powershell
pip install -r requirements.txt
# utwórz .env z kluczami API
# sklonuj data/repos/{requests,flask,httpie} i wygeneruj zrzuty radona (sekcja 4)

# wariant automatyczny:
python run_all.py

# ...albo ręcznie, krok po kroku (ta sama kolejność co w run_all.py):
python scripts\init_db.py
python scripts\init_db_v2.py
python scripts\sample_functions.py
python scripts\extract_snapshots.py
python scripts\measure_baseline.py
python scripts\setup_repo_venvs.py
python scripts\run_single_pass.py
python scripts\analysis\hypothesis_tests.py
```
