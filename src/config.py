from __future__ import annotations
import os
from pathlib import Path
try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv(*_args, **_kwargs) -> bool:
        return False
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / '.env')
RANDOM_SEED: int = int(os.getenv('RANDOM_SEED', '42'))
SAMPLE_PER_REPO: int = int(os.getenv('SAMPLE_PER_REPO', '35'))
MIN_CC_THRESHOLD: int = int(os.getenv('MIN_CC_THRESHOLD', '5'))
MAX_API_COST_USD: float = float(os.getenv('MAX_API_COST_USD', '20.0'))
DATA_DIR: Path = ROOT / os.getenv('DATA_DIR', 'data')
RESULTS_DIR: Path = ROOT / os.getenv('RESULTS_DIR', 'results')
LOGS_DIR: Path = ROOT / os.getenv('LOGS_DIR', 'logs')
DB_PATH: Path = ROOT / os.getenv('DB_PATH', 'results/results.db')
OPENAI_API_KEY: str | None = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY: str | None = os.getenv('ANTHROPIC_API_KEY')
GEMINI_API_KEY: str | None = os.getenv('GEMINI_API_KEY')
PRICING: dict[str,
              dict[str,
                   float]] = {'gpt-4o-2024-08-06': {'input': 2.5,
                                                    'output': 10.0},
                              'gemini-2.5-flash': {'input': 0.15,
                                                   'output': 0.6},
                              'claude-sonnet-4-6': {'input': 3.0,
                                                    'output': 15.0}}
MODELS: dict[str,
             dict[str,
                  str]] = {'A': {'provider': 'openai',
                                 'name': os.getenv('MODEL_OPENAI',
                                                   'gpt-4o-2024-08-06')},
                           'G': {'provider': 'gemini',
                                 'name': os.getenv('MODEL_GEMINI',
                                                   'gemini-2.5-flash')},
                           'C': {'provider': 'anthropic',
                                 'name': os.getenv('MODEL_ANTHROPIC',
                                                   'claude-sonnet-4-6')}}
BUDGET: dict[str, float] = {'openai': 5.0, 'anthropic': 10.0, 'gemini': 6.0}
