from __future__ import annotations
from _dataio import ANALYSIS_DIR, FIGURES_DIR, load_v2, write_summary
import sys
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, accuracy_score
from sklearn.model_selection import StratifiedKFold
from statsmodels.formula.api import logit
matplotlib.use('Agg')
sys.path.insert(0, str(Path(__file__).resolve().parent))


def _prepare(v2: pd.DataFrame) -> pd.DataFrame:
    df = v2[(v2['tests_targeted'].fillna(0) > 0) & v2['quality_score'].notna() &
            v2['semantic_score'].notna() & v2['changed_pct'].notna() & v2['cc_before'].notna()].copy()
    df['y'] = df['tests_green_strict'].astype(int)
    df['condition'] = df['condition'].astype('category')
    return df


def _fit_statsmodels(df: pd.DataFrame, formula: str) -> dict:
    model = logit(formula, data=df).fit(disp=0, maxiter=200)
    params = model.params
    conf = model.conf_int()
    odds = pd.DataFrame({'coef': params,
                         'se': model.bse,
                         'z': model.tvalues,
                         'p': model.pvalues,
                         'or': np.exp(params),
                         'or_low': np.exp(conf[0]),
                         'or_high': np.exp(conf[1])})
    return {'formula': formula, 'n': int(model.nobs), 'loglik': round(float(model.llf), 3), 'aic': round(float(model.aic), 3), 'bic': round(float(model.bic), 3), 'mcfadden_r2': round(float(1 - model.llf / model.llnull), 4), 'lr_pvalue': round(float(model.llr_pvalue), 6), 'coefficients': {
        name: {'coef': round(float(row['coef']), 4), 'se': round(float(row['se']), 4), 'z': round(float(row['z']), 3), 'p': round(float(row['p']), 6), 'or': round(float(row['or']), 4), 'or_ci': [round(float(row['or_low']), 4), round(float(row['or_high']), 4)]} for name, row in odds.iterrows()}}


def _cv_metrics(df: pd.DataFrame, predictors: list[str], *, drop_const: bool = False) -> dict:
    X_full = pd.get_dummies(df[predictors + ['condition']],
                            columns=['condition'], drop_first=True).astype(float)
    if drop_const and 'Intercept' in X_full.columns:
        X_full = X_full.drop(columns=['Intercept'])
    y = df['y'].to_numpy()
    if y.sum() < 5 or (1 - y).sum() < 5:
        return {'note': 'klasy zbyt rzadkie do CV',
                'n_pos': int(y.sum()), 'n_neg': int((1 - y).sum())}
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    aucs, accs, briers = ([], [], [])
    for train_idx, test_idx in skf.split(X_full, y):
        clf = LogisticRegression(max_iter=2000, solver='liblinear')
        clf.fit(X_full.iloc[train_idx], y[train_idx])
        probs = clf.predict_proba(X_full.iloc[test_idx])[:, 1]
        preds = (probs >= 0.5).astype(int)
        try:
            aucs.append(roc_auc_score(y[test_idx], probs))
        except ValueError:
            pass
        accs.append(accuracy_score(y[test_idx], preds))
        briers.append(brier_score_loss(y[test_idx], probs))
    return {'n_folds': 5, 'roc_auc_mean': round(float(np.mean(aucs)), 4) if aucs else None, 'roc_auc_std': round(float(np.std(
        aucs)), 4) if aucs else None, 'accuracy_mean': round(float(np.mean(accs)), 4), 'brier_mean': round(float(np.mean(briers)), 4)}


def plot_or_forest(models: dict[str, dict]) -> Path:
    fig, axes = plt.subplots(1, len(models), figsize=(5 * len(models), 5), sharey=False)
    if len(models) == 1:
        axes = [axes]
    for ax, (name, m) in zip(axes, models.items()):
        coef = m['coefficients']
        labels = [k for k in coef.keys() if k != 'Intercept']
        ors = [coef[k]['or'] for k in labels]
        lo = [coef[k]['or_ci'][0] for k in labels]
        hi = [coef[k]['or_ci'][1] for k in labels]
        y_pos = np.arange(len(labels))
        ax.errorbar(
            ors,
            y_pos,
            xerr=[
                np.array(ors) -
                np.array(lo),
                np.array(hi) -
                np.array(ors)],
            fmt='o',
            color='#1f77b4',
            capsize=4,
            markersize=6)
        ax.axvline(1.0, color='grey', linestyle=':', linewidth=0.8)
        ax.set_xscale('log')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_xlabel('Odds Ratio (95% CI)')
        ax.set_title(f"{name}\nAIC={m['aic']}, R²(McF)={m['mcfadden_r2']}", fontsize=11)
        ax.grid(axis='x', alpha=0.3)
    fig.suptitle(
        'Forest plot odds ratios - regresja logistyczna tests_green ~ predyktory',
        fontsize=12)
    fig.tight_layout()
    out = FIGURES_DIR / 'fig_logit_or.png'
    fig.savefig(out, dpi=200, bbox_inches='tight')
    plt.close(fig)
    return out


def render_md(payload: dict) -> str:
    md = ['# 5.A2 Regresja logistyczna: tests_green ~ predyktory\n']
    md.append('Cel: czy `quality_score` (LLM-judge) wnosi inkrementalna wartosc predykcyjna dla `tests_green_strict` PO kontroli na rozmiar zmiany (`changed_pct`), zlozonosc poczatkowa (`cc_before`) i warunek eksperymentu? To multivariate fortyfikacja H5.\n')
    md.append('## Porownanie modeli (information criteria)\n')
    md.append('| Model | Predyktory | n | LogLik | AIC | BIC | McFadden R² | LR p |')
    md.append('|---|---|---|---|---|---|---|---|')
    for name, m in payload['models'].items():
        md.append(
            f"| {name} | {m['formula']} | {m['n']} | {m['loglik']} | {m['aic']} | {m['bic']} | {m['mcfadden_r2']} | {m['lr_pvalue']} |")
    md.append('\n## Walidacja krzyzowa (5-fold stratified)\n')
    md.append('| Model | ROC AUC mean | AUC SD | Accuracy mean | Brier score |')
    md.append('|---|---|---|---|---|')
    for name, cv in payload['cv'].items():
        md.append(f"| {name} | {cv.get('roc_auc_mean', '-')} | {cv.get('roc_auc_std', '-')} | {cv.get('accuracy_mean', '-')} | {cv.get('brier_mean', '-')} |")
    for name, m in payload['models'].items():
        md.append(f'\n## {name} - szczegoly\n')
        md.append('| zmienna | coef | SE | z | p | OR | 95% CI |')
        md.append('|---|---|---|---|---|---|---|')
        for k, r in m['coefficients'].items():
            md.append(
                f"| {k} | {r['coef']} | {r['se']} | {r['z']} | {r['p']} | {r['or']} | [{r['or_ci'][0]}, {r['or_ci'][1]}] |")
    md.append('\n## Interpretacja\n')
    m1, m3 = (payload['models']['Model_1_main'], payload['models']['Model_3_baseline'])
    aic_diff = m1['aic'] - m3['aic']
    md.append(
        f'- Roznica AIC Model_1 (z quality_score) vs Model_3 (baseline): {aic_diff:+.2f}. Konwencja Burnham & Anderson: roznica > 2 = istotna; < 2 = modele rownowazne.\n')
    q_coef = m1['coefficients'].get('quality_score', {})
    md.append(
        f"- Wspolczynnik `quality_score` w Model_1: coef={q_coef.get('coef')}, p={q_coef.get('p')}, OR={q_coef.get('or')} (CI {q_coef.get('or_ci')}).\n")
    md.append('- Jesli OR(quality_score) ~ 1.0 i p > 0.05, to **LLM-judge nie wnosi informacji predykcyjnej po kontroli na rozmiar zmiany** - potwierdzenie H5 na poziomie multivariate.\n')
    return '\n'.join(md) + '\n'


def run() -> dict:
    v2 = load_v2(applied_only=True)
    df = _prepare(v2)
    formulas = {
        'Model_1_main': 'y ~ quality_score + changed_pct + cc_before + C(condition)',
        'Model_2_semantic': 'y ~ semantic_score + changed_pct + cc_before + C(condition)',
        'Model_3_baseline': 'y ~ changed_pct + cc_before + C(condition)'}
    cv_predictors = {
        'Model_1_main': [
            'quality_score', 'changed_pct', 'cc_before'], 'Model_2_semantic': [
            'semantic_score', 'changed_pct', 'cc_before'], 'Model_3_baseline': [
                'changed_pct', 'cc_before']}
    payload = {
        'n_observations': int(
            len(df)), 'n_pos': int(
            df['y'].sum()), 'n_neg': int(
                (1 - df['y']).sum()), 'models': {}, 'cv': {}}
    for name, formula in formulas.items():
        payload['models'][name] = _fit_statsmodels(df, formula)
        payload['cv'][name] = _cv_metrics(df, cv_predictors[name])
    fig = plot_or_forest(payload['models'])
    write_summary('logistic_regression', payload)
    out_md = ANALYSIS_DIR / 'logistic_regression.md'
    out_md.write_text(render_md(payload), encoding='utf-8')
    print(f"[logit] summary -> {ANALYSIS_DIR / 'logistic_regression.json'}")
    print(f'[logit] report  -> {out_md}')
    print(f'[logit] forest  -> {fig}')
    print(
        f"\nn={payload['n_observations']}, n_pos (tests_green)={payload['n_pos']}, n_neg={payload['n_neg']}")
    print(
        '\nAIC: Model_1 (with quality_score) =',
        payload['models']['Model_1_main']['aic'],
        '  vs  Model_3 (baseline) =',
        payload['models']['Model_3_baseline']['aic'])
    q = payload['models']['Model_1_main']['coefficients'].get('quality_score', {})
    print(f"quality_score in Model_1: OR={q.get('or')}, p={q.get('p')}, CI={q.get('or_ci')}")
    return payload


if __name__ == '__main__':
    run()
