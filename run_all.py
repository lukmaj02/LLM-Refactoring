"""Orchestrator uruchamiajacy caly pipeline eksperymentu od poczatku do konca.

Uruchamia po kolei: inicjalizacje bazy, losowanie probek, ekstrakcje snapshotow,
pomiar bazowy, budowe srodowisk testowych, glowny przebieg (Faza 4C) oraz analize.

Przyklady:
    python run_all.py                      # pelny pipeline
    python run_all.py --list               # pokaz kroki i zakonicz
    python run_all.py --dry-run            # pokaz plan bez uruchamiania
    python run_all.py --skip-analysis      # bez fazy analizy
    python run_all.py --only run_single_pass
    python run_all.py --start-at sample_functions --stop-after measure_baseline
    python run_all.py --limit 5 --conditions T A   # przekazane do run_single_pass
    python run_all.py --skip-venvs --continue-on-error
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
ANALYSIS = SCRIPTS / "analysis"
DATA = ROOT / "data"
REPOS = ("requests", "flask", "httpie")


def _ok(msg: str = "") -> tuple[bool, str]:
    return True, msg


def check_repos() -> tuple[bool, str]:
    missing = [r for r in REPOS if not (DATA / "repos" / r).is_dir()]
    if missing:
        return False, (
            f"brak sklonowanych repozytoriow w data/repos/: {', '.join(missing)}. "
            "Sklonuj requests, flask i httpie do data/repos/<nazwa>."
        )
    return _ok()


def check_radon_dumps() -> tuple[bool, str]:
    missing = []
    for r in REPOS:
        for suffix in ("cc_raw", "mi_raw"):
            p = DATA / "results" / f"{r}_{suffix}.json"
            if not p.is_file():
                missing.append(p.relative_to(ROOT).as_posix())
    if missing:
        cmds = "\n".join(
            f"    radon cc data/repos/{r} -s --json > data/results/{r}_cc_raw.json\n"
            f"    radon mi data/repos/{r} --json > data/results/{r}_mi_raw.json"
            for r in REPOS
        )
        return False, (
            "brak surowych zrzutow radona wymaganych przez sample_functions:\n    "
            + "\n    ".join(missing)
            + "\nWygeneruj je np. tak:\n"
            + cmds
        )
    return _ok()


def check_samples() -> tuple[bool, str]:
    p = DATA / "samples" / "functions_sample.json"
    if not p.is_file():
        return False, "brak data/samples/functions_sample.json - uruchom krok sample_functions."
    return _ok()


def check_snapshots() -> tuple[bool, str]:
    p = DATA / "snapshots" / "index.json"
    if not p.is_file():
        return False, "brak data/snapshots/index.json - uruchom krok extract_snapshots."
    return _ok()


def check_venvs() -> tuple[bool, str]:
    p = DATA / "venvs" / "manifest.json"
    if not p.is_file():
        return False, "brak data/venvs/manifest.json - uruchom krok setup_repo_venvs."
    return _ok()


def check_api_keys() -> tuple[bool, str]:
    keys = ("OPENAI_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY")
    if any(os.getenv(k) for k in keys):
        return _ok()
    env_file = ROOT / ".env"
    if env_file.is_file():
        text = env_file.read_text(encoding="utf-8", errors="ignore")
        if any(k in text for k in keys):
            return _ok()
    return False, (
        "nie wykryto zadnego klucza API (OPENAI/GEMINI/ANTHROPIC) w srodowisku ani .env. "
        "Warunki A/G/C beda odrzucane. Uzupelnij .env przed pelnym przebiegiem."
    )


@dataclass
class Step:
    id: str
    title: str
    argv: list[str]
    category: str = "core"
    critical: bool = True
    checks: list[Callable[[], tuple[bool, str]]] = field(default_factory=list)


def build_steps(args: argparse.Namespace) -> list[Step]:
    py = sys.executable

    single_pass = [py, str(SCRIPTS / "run_single_pass.py")]
    if args.limit is not None:
        single_pass += ["--limit", str(args.limit)]
    if args.conditions:
        single_pass += ["--conditions", *args.conditions]

    steps: list[Step] = [
        Step("init_db", "Inicjalizacja bazy (tabele bazowe)",
             [py, str(SCRIPTS / "init_db.py")], "setup"),
        Step("init_db_v2", "Inicjalizacja tabeli experiment_results_v2",
             [py, str(SCRIPTS / "init_db_v2.py")], "setup"),
        Step("sample_functions", "Losowanie probek funkcji",
             [py, str(SCRIPTS / "sample_functions.py")], "data",
             checks=[check_repos, check_radon_dumps]),
        Step("extract_snapshots", "Ekstrakcja snapshotow funkcji",
             [py, str(SCRIPTS / "extract_snapshots.py")], "data",
             checks=[check_samples]),
        Step("measure_baseline", "Pomiar bazowy (warunek K)",
             [py, str(SCRIPTS / "measure_baseline.py")], "data",
             checks=[check_snapshots]),
        Step("setup_repo_venvs", "Budowa izolowanych venvow repozytoriow",
             [py, str(SCRIPTS / "setup_repo_venvs.py")], "setup",
             checks=[check_repos]),
        Step("run_single_pass", "Glowny przebieg eksperymentu (Faza 4C)",
             single_pass, "experiment",
             checks=[check_snapshots, check_venvs, check_api_keys]),
    ]

    analysis_scripts = [
        ("eda", "Analiza eksploracyjna"),
        ("hypothesis_tests", "Testy hipotez"),
        ("effect_sizes", "Wielkosci efektu"),
        ("correlations", "Korelacje"),
        ("per_repo", "Analiza per repozytorium"),
        ("logistic_regression", "Regresja logistyczna"),
        ("power_analysis", "Analiza mocy"),
        ("compile_but_break", "Kompiluje-ale-psuje"),
        ("test_retest", "Test-retest"),
        ("judge_retest_analysis", "Judge retest"),
        ("judge_cross_analysis", "Judge cross-analysis"),
        ("rerun_gate_analysis", "Analiza bramki testowej"),
        ("thesis_numbers", "Liczby do pracy"),
        ("thesis_figures", "Wykresy do pracy"),
        ("final_figures", "Wykresy koncowe"),
    ]
    for name, title in analysis_scripts:
        steps.append(
            Step(f"analysis:{name}", title,
                 [py, str(ANALYSIS / f"{name}.py")], "analysis", critical=False)
        )

    return steps


def select_steps(steps: list[Step], args: argparse.Namespace) -> list[Step]:
    ids = [s.id for s in steps]

    def resolve(token: str) -> list[str]:
        if token in ids:
            return [token]
        matches = [i for i in ids if i == token or i.endswith(f":{token}")]
        if not matches:
            sys.exit(f"[run_all] nieznany krok: {token}\nDostepne: {', '.join(ids)}")
        return matches

    selected = steps
    if args.only:
        wanted = {m for tok in args.only for m in resolve(tok)}
        selected = [s for s in selected if s.id in wanted]
    if args.start_at:
        start = resolve(args.start_at)[0]
        idx = next(i for i, s in enumerate(selected) if s.id == start)
        selected = selected[idx:]
    if args.stop_after:
        stop = resolve(args.stop_after)[0]
        idx = next((i for i, s in enumerate(selected) if s.id == stop), None)
        if idx is not None:
            selected = selected[: idx + 1]
    if args.skip:
        skip = {m for tok in args.skip for m in resolve(tok)}
        selected = [s for s in selected if s.id not in skip]
    if args.skip_analysis:
        selected = [s for s in selected if s.category != "analysis"]
    if args.skip_venvs:
        selected = [s for s in selected if s.id != "setup_repo_venvs"]
    return selected


def run_step(step: Step, args: argparse.Namespace) -> tuple[str, float]:
    print("\n" + "=" * 70)
    print(f"[{step.id}] {step.title}")
    print("=" * 70)

    for check in step.checks:
        ok, msg = check()
        if not ok:
            if args.force:
                print(f"[UWAGA] {msg}\n[run_all] --force: kontynuuje mimo to.")
            else:
                print(f"[BLAD] prerekwizyt niespelniony: {msg}")
                return "PREREQ", 0.0

    if args.dry_run:
        print("  (dry-run) " + " ".join(step.argv))
        return "DRY", 0.0

    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env.setdefault("PYTHONIOENCODING", "utf-8")

    start = time.time()
    proc = subprocess.run(step.argv, cwd=str(ROOT), env=env)
    elapsed = time.time() - start

    status = "OK" if proc.returncode == 0 else "FAILED"
    print(f"\n[{step.id}] -> {status} ({elapsed:.1f}s, exit={proc.returncode})")
    return status, elapsed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Uruchom caly pipeline eksperymentu (setup -> dane -> przebieg -> analiza).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--list", action="store_true", help="wypisz kroki i zakoncz")
    parser.add_argument("--dry-run", action="store_true", help="pokaz plan bez uruchamiania")
    parser.add_argument("--only", nargs="+", metavar="STEP", help="uruchom tylko wskazane kroki")
    parser.add_argument("--start-at", metavar="STEP", help="zacznij od tego kroku")
    parser.add_argument("--stop-after", metavar="STEP", help="zakoncz po tym kroku")
    parser.add_argument("--skip", nargs="+", metavar="STEP", help="pomin wskazane kroki")
    parser.add_argument("--skip-analysis", action="store_true", help="pomin faze analizy")
    parser.add_argument("--skip-venvs", action="store_true", help="pomin budowe venvow")
    parser.add_argument("--continue-on-error", action="store_true",
                        help="nie przerywaj przy bledzie kroku krytycznego")
    parser.add_argument("--force", action="store_true",
                        help="ignoruj niespelnione prerekwizyty")
    parser.add_argument("--limit", type=int, help="limit probek (przekazany do run_single_pass)")
    parser.add_argument("--conditions", nargs="+", metavar="C",
                        help="warunki dla run_single_pass, np. --conditions T A")
    args = parser.parse_args()

    steps = build_steps(args)
    selected = select_steps(steps, args)

    if args.list:
        print("Kroki pipeline (w kolejnosci):\n")
        for s in steps:
            mark = " " if s in selected else "-"
            crit = "" if s.critical else "  [niekrytyczny]"
            print(f"  [{mark}] {s.id:<28} {s.title}{crit}")
        return 0

    if not selected:
        print("[run_all] nie wybrano zadnego kroku.")
        return 1

    print(f"[run_all] Zaplanowano {len(selected)} krokow. "
          f"Interpreter: {sys.executable}")
    results: list[tuple[str, str, float]] = []
    total_start = time.time()

    for step in selected:
        status, elapsed = run_step(step, args)
        results.append((step.id, status, elapsed))
        failed = status in ("FAILED", "PREREQ")
        if failed and step.critical and not args.continue_on_error and not args.dry_run:
            print(f"\n[run_all] Krok krytyczny '{step.id}' zakonczyl sie bledem - przerywam.")
            break

    total = time.time() - total_start
    print("\n" + "=" * 70)
    print("PODSUMOWANIE")
    print("=" * 70)
    for sid, status, elapsed in results:
        print(f"  {status:<8} {sid:<28} {elapsed:6.1f}s")
    print(f"\nLaczny czas: {total:.1f}s")

    if args.dry_run:
        return 0
    any_fail = any(st in ("FAILED", "PREREQ") for _, st, _ in results)
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
