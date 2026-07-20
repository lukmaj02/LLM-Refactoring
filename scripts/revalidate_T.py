import json
import sqlite3
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.config import DB_PATH, DATA_DIR
from src.arp_pipeline import ARPPipeline


def load_samples():
    path = DATA_DIR / 'samples' / 'functions_sample.json'
    return {s['sample_id']: s for s in json.loads(path.read_text(encoding='utf-8'))}


conn = sqlite3.connect(str(DB_PATH))
rows = conn.execute(
    "SELECT sample_id FROM experiment_results WHERE condition='T' AND rejection_reason='too_large'").fetchall()
conn.close()
sample_ids = [r[0] for r in rows]
print(f'T too_large samples: {sample_ids}')
if not sample_ids:
    print('Nothing to do.')
    sys.exit(0)
samples = load_samples()
pipeline = ARPPipeline()
for sid in sample_ids:
    sample = samples[sid]
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("DELETE FROM experiment_results WHERE sample_id=? AND condition='T'", (sid,))
    conn.commit()
    conn.close()
    result = pipeline.run(sample, 'T')
    print(f'  {sid}: {result.decision} (error={result.error})')
conn = sqlite3.connect(str(DB_PATH))
t_acc = conn.execute(
    "SELECT COUNT(*) FROM experiment_results WHERE condition='T' AND patch_accepted=1").fetchone()[0]
t_tl = conn.execute(
    "SELECT COUNT(*) FROM experiment_results WHERE condition='T' AND rejection_reason='too_large'").fetchone()[0]
print(f'\nT: accepted={t_acc}, too_large={t_tl}')
conn.close()
