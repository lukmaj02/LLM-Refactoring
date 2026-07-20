from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'progress' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
DPI = 200
TITLE_FS = 14
LABEL_FS = 13
TICK_FS = 12
LEGEND_FS = 11
MODELS_SHORT = ('GPT-4o', 'Gemini 2.5 Flash', 'Claude Sonnet 4.6')
ACCEPT_BEFORE = (14, 10, 7)
ACCEPT_AFTER = (81, 46, 70)
CC_BEFORE_AVG = (10.5, 9.7, 11.3)
CC_AFTER_AVG = (4.9, 4.1, 5.3)
QUALITY_PART1 = {'Ogólna jakość': (7.6, 7.0, 8.3), 'SOLID': (7.6, 7.2, 7.6), 'DRY': (5.6, 5.5, 5.9)}
QUALITY_PART2 = {'KISS': (7.5, 7.4, 8.1), 'Równoważność semantyczna': (9.2, 7.6, 9.9)}
REJECTION_SYNERR = (0, 29, 0)
MI_BEFORE_AVG = (78.9, 80.6, 77.8)
MI_AFTER_AVG = (68.1, 83.2, 71.2)
REPOS = ('requests', 'httpie', 'flask')
CICD_BASELINE = (11.1, 0.7, 2.1)
CICD_ARP = (15.2, 4.8, 6.1)
REJECTIONS = {'Zaakceptowane': (81, 46, 70), 'Brak poprawy metryki': (22, 6, 14), 'Model odmówił': (
    2, 15, 21), 'Błąd składni': (0, 29, 0), 'Inne (API / timeout)': (0, 9, 0)}
COSTS = {'GPT-4o': 1.52, 'Gemini 2.5 Flash': 0.1, 'Claude Sonnet 4.6': 2.78}


def style_axes(ax, title: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=TITLE_FS, pad=12)
    ax.set_ylabel(ylabel, fontsize=LABEL_FS)
    ax.tick_params(axis='both', labelsize=TICK_FS)
    ax.grid(axis='y', alpha=0.35)


def fig_acceptance_before_after() -> None:
    x = range(len(MODELS_SHORT))
    w = 0.35
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar([i - w / 2 for i in x], ACCEPT_BEFORE, width=w,
           label='Przed korektą metodyki', color='#95a5a6')
    ax.bar([i + w / 2 for i in x], ACCEPT_AFTER, width=w,
           label='Po usunięciu bramy rozmiaru patcha', color='#2980b9')
    ax.set_xticks(list(x))
    ax.set_xticklabels(MODELS_SHORT, fontsize=TICK_FS)
    ax.set_ylim(0, 105)
    ax.axhline(105, color='#bdc3c7', linestyle='--', linewidth=0.8)
    style_axes(
        ax,
        'Liczba zaakceptowanych refaktoryzacji na 105 funkcji badanych',
        'Liczba próbek (maksimum 105)')
    ax.legend(loc='upper left', fontsize=LEGEND_FS)
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_akceptacja_przed_po.png', dpi=DPI)
    plt.close(fig)


def fig_cc_reduction() -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(MODELS_SHORT))
    w = 0.35
    ax.bar([i - w / 2 for i in x], CC_BEFORE_AVG, width=w,
           label='Przed refaktoryzacją (średnia)', color='#e67e22')
    ax.bar([i + w / 2 for i in x], CC_AFTER_AVG, width=w,
           label='Po refaktoryzacji (średnia)', color='#27ae60')
    ax.set_xticks(list(x))
    ax.set_xticklabels(MODELS_SHORT, fontsize=TICK_FS)
    style_axes(ax, 'Złożoność cyklomatyczna (Radon, McCabe) — tylko zaakceptowane próbki',
               'Wartość średnia złożoności cyklomatycznej')
    ax.legend(loc='upper right', fontsize=LEGEND_FS)
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_zlozonosc_cyklomatyczna.png', dpi=DPI)
    plt.close(fig)


def _fig_quality_bars(
        quality_dict: dict[str, tuple[float, float, float]], fname: str, chart_title: str) -> None:
    dims = list(quality_dict.keys())
    fig, ax = plt.subplots(figsize=(11, 6))
    w = 0.25
    offsets = [-w, 0, w]
    colors = ('#3498db', '#9b59b6', '#e74c3c')
    x_base = range(len(dims))
    for j, model in enumerate(MODELS_SHORT):
        vals = [quality_dict[d][j] for d in dims]
        pos = [i + offsets[j] for i in x_base]
        ax.bar(pos, vals, width=w, label=model, color=colors[j])
    ax.set_xticks(list(x_base))
    ax.set_xticklabels(dims, fontsize=TICK_FS)
    ax.set_ylim(0, 10.5)
    ax.axhline(10, color='#ecf0f1', linestyle='--', linewidth=0.6)
    style_axes(ax, chart_title, 'Średnia ocena (skala 0–10)')
    ax.legend(loc='upper right', fontsize=LEGEND_FS, ncol=3)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=DPI)
    plt.close(fig)


def fig_quality_dimensions_split() -> None:
    _fig_quality_bars(QUALITY_PART1, 'wykres_oceny_jakosci_czesc1.png',
                      'Oceny jakości (część 1) — model sędzia: Gemini 2.5 Flash')
    _fig_quality_bars(QUALITY_PART2, 'wykres_oceny_jakosci_czesc2.png',
                      'Oceny jakości (część 2) — model sędzia: Gemini 2.5 Flash')


def fig_maintainability_index() -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(MODELS_SHORT))
    w = 0.35
    ax.bar([i - w / 2 for i in x], MI_BEFORE_AVG, width=w,
           label='Przed refaktoryzacją (średnia)', color='#8e44ad')
    ax.bar([i + w / 2 for i in x], MI_AFTER_AVG, width=w,
           label='Po refaktoryzacji (średnia)', color='#16a085')
    ax.set_xticks(list(x))
    ax.set_xticklabels(MODELS_SHORT, fontsize=TICK_FS)
    style_axes(
        ax,
        'Indeks utrzymywalności kodu (narzędzie Radon, skala 0–100) — zaakceptowane próbki',
        'Wartość średnia indeksu utrzymywalności')
    ax.legend(loc='best', fontsize=LEGEND_FS)
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_indeks_utrzymywalnosci.png', dpi=DPI)
    plt.close(fig)


def fig_syntax_errors() -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    colors_bar = ('#3498db', '#9b59b6', '#e74c3c')
    ax.bar(MODELS_SHORT, REJECTION_SYNERR, color=colors_bar)
    style_axes(
        ax,
        'Liczba odrzuć ze względu na błąd składni Python po wygenerowaniu kodu',
        'Liczba próbek (na 105 badanych funkcji)')
    for i, v in enumerate(REJECTION_SYNERR):
        ax.text(i, v + 0.8, str(v), ha='center', fontsize=13, fontweight='bold')
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_bledy_skladni.png', dpi=DPI)
    plt.close(fig)


def fig_cicd_overhead() -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(REPOS))
    w = 0.35
    ax.bar([i - w / 2 for i in x], CICD_BASELINE, width=w,
           label='Potok bazowy (bez ARP)', color='#2c3e50')
    ax.bar([i + w / 2 for i in x], CICD_ARP, width=w, label='Potok z ARP', color='#e74c3c')
    for i in x:
        overhead_pct = (CICD_ARP[i] - CICD_BASELINE[i]) / CICD_BASELINE[i] * 100
        ax.annotate(
            f'+{CICD_ARP[i] - CICD_BASELINE[i]:.1f}s\n(+{overhead_pct:.0f}%)',
            xy=(
                i + w / 2,
                CICD_ARP[i]),
            xytext=(
                0,
                6),
            textcoords='offset points',
            ha='center',
            fontsize=10,
            color='#c0392b',
            fontweight='bold')
    ax.set_xticks(list(x))
    ax.set_xticklabels(REPOS, fontsize=TICK_FS)
    style_axes(ax, 'Narzut etapu ARP na czas trwania potoku CI/CD',
               'Średni czas trwania potoku (sekundy)')
    ax.legend(loc='upper right', fontsize=LEGEND_FS)
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_narzut_cicd.png', dpi=DPI)
    plt.close(fig)


def fig_rejection_reasons() -> None:
    import numpy as np
    categories = list(REJECTIONS.keys())
    a_vals = [REJECTIONS[c][0] for c in categories]
    g_vals = [REJECTIONS[c][1] for c in categories]
    c_vals = [REJECTIONS[c][2] for c in categories]
    fig, ax = plt.subplots(figsize=(12, 6))
    y = np.arange(len(MODELS_SHORT))
    h = 0.6
    colors = ['#27ae60', '#f39c12', '#8e44ad', '#e74c3c', '#95a5a6']
    left_a = np.zeros(1)
    left_g = np.zeros(1)
    left_c = np.zeros(1)
    all_data = [a_vals, g_vals, c_vals]
    for idx, cat in enumerate(categories):
        vals = [all_data[m][idx] for m in range(3)]
        lefts = [sum(all_data[m][:idx]) for m in range(3)]
        bars = ax.barh(y, vals, height=h, left=lefts, label=cat, color=colors[idx])
        for bar, v in zip(bars, vals):
            if v > 3:
                ax.text(
                    bar.get_x() +
                    bar.get_width() /
                    2,
                    bar.get_y() +
                    bar.get_height() /
                    2,
                    str(v),
                    ha='center',
                    va='center',
                    fontsize=10,
                    fontweight='bold',
                    color='white')
    ax.set_yticks(list(y))
    ax.set_yticklabels(MODELS_SHORT, fontsize=TICK_FS)
    ax.set_xlabel('Liczba próbek (na 105 per model)', fontsize=LABEL_FS)
    ax.set_title('Rozkład wyników walidacji refaktoryzacji per model AI', fontsize=TITLE_FS, pad=12)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12),
              ncol=3, fontsize=LEGEND_FS, frameon=True)
    ax.grid(axis='x', alpha=0.35)
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_przyczyny_odrzucen.png', dpi=DPI, bbox_inches='tight')
    plt.close(fig)


def fig_model_costs() -> None:
    models = list(COSTS.keys())
    values = list(COSTS.values())
    colors = ('#3498db', '#9b59b6', '#e74c3c')
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(models, values, color=colors, width=0.5)
    for bar, v in zip(bars, values):
        ax.text(
            bar.get_x() +
            bar.get_width() /
            2,
            bar.get_height() +
            0.05,
            f'${v:.2f}',
            ha='center',
            fontsize=13,
            fontweight='bold')
    style_axes(ax, 'Całkowity koszt API per model (eksperyment + rewalidacja)', 'Koszt (USD)')
    ax.set_ylim(0, max(values) * 1.25)
    fig.tight_layout()
    fig.savefig(OUT / 'wykres_koszty_modeli.png', dpi=DPI)
    plt.close(fig)


def main() -> None:
    fig_acceptance_before_after()
    fig_cc_reduction()
    fig_maintainability_index()
    fig_quality_dimensions_split()
    fig_syntax_errors()
    fig_cicd_overhead()
    fig_rejection_reasons()
    fig_model_costs()
    legacy = OUT / 'wykres_oceny_jakosci_wymiary.png'
    if legacy.exists():
        legacy.unlink()
    print(f"Zapisano {len(list(OUT.glob('*.png')))} wykresów w: {OUT}")


if __name__ == '__main__':
    main()
