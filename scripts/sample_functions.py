from __future__ import annotations
import json
import random
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import RANDOM_SEED
REPOS = {
    'requests': {
        'cc_raw': ROOT / 'data' / 'results' / 'requests_cc_raw.json',
        'mi_raw': ROOT / 'data' / 'results' / 'requests_mi_raw.json'},
    'httpie': {
        'cc_raw': ROOT / 'data' / 'results' / 'httpie_cc_raw.json',
        'mi_raw': ROOT / 'data' / 'results' / 'httpie_mi_raw.json'},
    'flask': {
        'cc_raw': ROOT / 'data' / 'results' / 'flask_cc_raw.json',
        'mi_raw': ROOT / 'data' / 'results' / 'flask_mi_raw.json'}}
SAMPLE_PER_REPO = 35
TIERS = {
    'high': {
        'min_cc': 10, 'share': 0.5}, 'mid': {
            'min_cc': 5, 'max_cc': 9, 'share': 0.3}, 'low': {
                'min_cc': 1, 'max_cc': 4, 'share': 0.2}}
MIN_LOC = 5


def load_mi_map(mi_path: Path) -> dict[str, float]:
    with open(mi_path) as f:
        data = json.load(f)
    return {fp: val for fp, val in data.items()}


def classify_tier(cc: int) -> str:
    if cc >= 10:
        return 'high'
    elif cc >= 5:
        return 'mid'
    else:
        return 'low'


def extract_candidates(cc_path: Path, mi_map: dict) -> list[dict]:
    with open(cc_path) as f:
        data = json.load(f)
    candidates = []
    for file_path, blocks in data.items():
        if 'test' in file_path.lower():
            continue
        for block in blocks:
            if block.get('type') not in ('function', 'method'):
                continue
            cc = block.get('complexity', 0)
            start = block.get('lineno', 0)
            end = block.get('endline', 0)
            loc = end - start + 1
            if loc < MIN_LOC:
                continue
            if cc < 1:
                continue
            func_name = block.get('name', '')
            classname = block.get('classname', '')
            full_name = f'{classname}.{func_name}' if classname else func_name
            norm_path = file_path.replace('\\', '/')
            mi_val = None
            for mi_key, mi_score in mi_map.items():
                mi_key_norm = mi_key.replace('\\', '/')
                if mi_key_norm == norm_path or mi_key_norm.endswith('/' + norm_path.split('/')[-1]):
                    mi_val = mi_score if isinstance(mi_score, (int, float)) else None
                    break
            candidates.append({'file_path': norm_path,
                               'function_name': full_name,
                               'start_line': start,
                               'end_line': end,
                               'cc': cc,
                               'mi': round(mi_val,
                                           1) if mi_val is not None else None,
                               'loc': loc,
                               'cc_tier': classify_tier(cc)})
    return candidates


def stratified_sample(candidates: list[dict], n: int, rng: random.Random) -> list[dict]:
    by_tier = {'high': [], 'mid': [], 'low': []}
    for c in candidates:
        by_tier[c['cc_tier']].append(c)
    targets = {
        'high': round(
            n * TIERS['high']['share']),
        'mid': round(
            n * TIERS['mid']['share']),
        'low': round(
            n * TIERS['low']['share'])}
    total_target = sum(targets.values())
    if total_target < n:
        targets['high'] += n - total_target
    elif total_target > n:
        targets['low'] -= total_target - n
    sampled = []
    for tier in ('high', 'mid', 'low'):
        pool = by_tier[tier]
        target = targets[tier]
        if len(pool) <= target:
            sampled.extend(pool)
        else:
            sampled.extend(rng.sample(pool, target))
    if len(sampled) < n:
        used = {(s['file_path'], s['function_name'], s['start_line']) for s in sampled}
        remaining = [
            c for c in candidates if (
                c['file_path'],
                c['function_name'],
                c['start_line']) not in used]
        rng.shuffle(remaining)
        sampled.extend(remaining[:n - len(sampled)])
    return sampled[:n]


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    all_samples: list[dict] = []
    counter = {}
    for repo_name, paths in REPOS.items():
        mi_map = load_mi_map(paths['mi_raw'])
        candidates = extract_candidates(paths['cc_raw'], mi_map)
        print(f"[sample] {repo_name}: {len(candidates)} candidates (high={sum((1 for c in candidates if c['cc_tier'] == 'high'))}, mid={sum((1 for c in candidates if c['cc_tier'] == 'mid'))}, low={sum((1 for c in candidates if c['cc_tier'] == 'low'))})")
        sampled = stratified_sample(candidates, SAMPLE_PER_REPO, rng)
        counter[repo_name] = 0
        for s in sampled:
            counter[repo_name] += 1
            s['repo'] = repo_name
            s['sample_id'] = f'{repo_name}_{counter[repo_name]:03d}'
        tiers = {t: sum((1 for s in sampled if s['cc_tier'] == t)) for t in ('high', 'mid', 'low')}
        print(
            f"  -> sampled {len(sampled)}: high={tiers['high']}, mid={tiers['mid']}, low={tiers['low']}")
        all_samples.extend(sampled)
    out_path = ROOT / 'data' / 'samples' / 'functions_sample.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(all_samples, f, indent=2)
    ids = [s['sample_id'] for s in all_samples]
    assert len(ids) == len(set(ids)), 'Duplicate sample_ids found!'
    assert len(all_samples) == SAMPLE_PER_REPO * \
        len(REPOS), f'Expected {SAMPLE_PER_REPO * len(REPOS)}, got {len(all_samples)}'
    print(f'\n[sample] Total: {len(all_samples)} functions saved to {out_path}')


if __name__ == '__main__':
    main()
