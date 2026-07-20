from __future__ import annotations
import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any
from src.ai_client import AIClient
from src.config import MODELS
log = logging.getLogger(__name__)
QUALITY_SYSTEM_PROMPT = 'You are a senior software engineer reviewing a Python code refactoring.\nYou will be given the ORIGINAL code and the REFACTORED code.\nEvaluate the refactoring quality on five dimensions, each scored 0-10.\n\nScoring guidelines:\n- **SOLID** (0-10): Does the refactoring improve adherence to SOLID principles?\n  0 = violates principles, 5 = neutral, 10 = significantly improves SRP/OCP/etc.\n- **DRY** (0-10): Does the refactoring reduce code duplication?\n  0 = adds duplication, 5 = neutral, 10 = eliminates significant repetition.\n- **KISS** (0-10): Does the refactoring simplify the code logic?\n  0 = more complex, 5 = neutral, 10 = dramatically simpler.\n- **Semantic Equivalence** (0-10): Does the refactored code preserve original behaviour?\n  0 = clearly broken, 5 = uncertain, 10 = provably equivalent.\n- **Overall Quality** (0-10): Overall assessment of the refactoring value.\n  0 = harmful, 5 = neutral, 10 = excellent improvement.\n\nReturn ONLY a valid JSON object with exactly these keys:\n{\n  "solid_score": <int 0-10>,\n  "dry_score": <int 0-10>,\n  "kiss_score": <int 0-10>,\n  "semantic_score": <int 0-10>,\n  "overall_score": <int 0-10>,\n  "rationale": "<1-2 sentence explanation>"\n}\n'
QUALITY_USER_PROMPT = '## ORIGINAL CODE:\n```python\n{original_code}\n```\n\n## REFACTORED CODE:\n```python\n{refactored_code}\n```\n\nEvaluate this refactoring. Return ONLY the JSON object.\n'


@dataclass
class QualityScore:
    solid_score: int
    dry_score: int
    kiss_score: int
    semantic_score: int
    overall_score: int
    rationale: str
    cost_usd: float = 0.0


def _parse_quality_response(text: str) -> dict[str, Any]:
    text = text.strip()
    json_match = re.search('\\{[^{}]*\\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    return json.loads(text)


def _clamp(val: Any, lo: int = 0, hi: int = 10) -> int:
    try:
        return max(lo, min(hi, int(val)))
    except (ValueError, TypeError):
        return 5


class QualityValidator:

    def __init__(self, model_condition: str = 'G') -> None:
        self._client = AIClient(max_retries=5, base_delay=3.0)
        self._model_cfg = MODELS[model_condition]

    @property
    def total_cost(self) -> float:
        return self._client.total_cost

    def evaluate(self, original_code: str, refactored_code: str) -> QualityScore:
        messages = [{'role': 'system',
                     'content': QUALITY_SYSTEM_PROMPT},
                    {'role': 'user',
                     'content': QUALITY_USER_PROMPT.format(original_code=original_code,
                                                           refactored_code=refactored_code)}]
        resp = self._client.complete(messages, self._model_cfg)
        try:
            data = _parse_quality_response(resp.content)
        except (json.JSONDecodeError, ValueError) as exc:
            log.warning('Failed to parse quality response: %s', exc)
            return QualityScore(solid_score=5, dry_score=5, kiss_score=5, semantic_score=5,
                                overall_score=5, rationale=f'PARSE_ERROR: {exc}', cost_usd=resp.cost_usd)
        return QualityScore(solid_score=_clamp(data.get('solid_score')), dry_score=_clamp(data.get('dry_score')), kiss_score=_clamp(data.get('kiss_score')), semantic_score=_clamp(
            data.get('semantic_score')), overall_score=_clamp(data.get('overall_score')), rationale=str(data.get('rationale', ''))[:500], cost_usd=resp.cost_usd)
