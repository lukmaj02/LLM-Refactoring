from __future__ import annotations
import logging
import time
from dataclasses import dataclass, field
from typing import Any
from src.config import ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, PRICING
log = logging.getLogger(__name__)


@dataclass
class AIResponse:
    content: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    response_time_s: float
    refused: bool
    model: str
    raw: Any = field(default=None, repr=False)


def _estimate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    p = PRICING.get(model)
    if p is None:
        return 0.0
    return (tokens_in * p['input'] + tokens_out * p['output']) / 1000000


class AIClient:

    def __init__(self, max_retries: int = 5, base_delay: float = 3.0) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._total_cost: float = 0.0

    @property
    def total_cost(self) -> float:
        return self._total_cost

    def complete(self, messages: list[dict[str, str]], model_config: dict[str, str],
                 *, temperature: float | None = None, max_tokens: int = 4096) -> AIResponse:
        provider = model_config['provider']
        dispatch = {
            'openai': self._call_openai,
            'gemini': self._call_gemini,
            'anthropic': self._call_anthropic}
        fn = dispatch.get(provider)
        if fn is None:
            raise ValueError(f'Unknown provider: {provider}')
        last_exc: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                resp = fn(messages, model_config, temperature=temperature, max_tokens=max_tokens)
                self._total_cost += resp.cost_usd
                return resp
            except Exception as exc:
                last_exc = exc
                delay = self._base_delay * 2 ** (attempt - 1)
                log.warning('Attempt %d/%d for %s failed: %s — retrying in %.1fs',
                            attempt, self._max_retries, provider, exc, delay)
                time.sleep(delay)
        raise RuntimeError(f'All {self._max_retries} attempts failed for {provider}') from last_exc

    def _call_openai(self, messages: list[dict[str, str]], model_config: dict[str, str],
                     *, temperature: float | None = None, max_tokens: int = 4096) -> AIResponse:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        model_name = model_config['name']
        temp = 0.2 if temperature is None else temperature
        t0 = time.perf_counter()
        resp = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temp,
            max_tokens=max_tokens)
        elapsed = time.perf_counter() - t0
        content = resp.choices[0].message.content or ''
        tokens_in = resp.usage.prompt_tokens if resp.usage else 0
        tokens_out = resp.usage.completion_tokens if resp.usage else 0
        cost = _estimate_cost(model_name, tokens_in, tokens_out)
        return AIResponse(content=content.strip(), tokens_in=tokens_in, tokens_out=tokens_out,
                          cost_usd=cost, response_time_s=round(elapsed, 3), refused=False, model=model_name, raw=resp)

    def _call_gemini(self, messages: list[dict[str, str]], model_config: dict[str, str],
                     *, temperature: float | None = None, max_tokens: int = 4096) -> AIResponse:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        model_name = model_config['name']
        system_text = self._extract_system(messages) or None
        temp = 0.2 if temperature is None else temperature
        contents = self._to_gemini_contents(messages)
        config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=max_tokens,
            system_instruction=system_text)
        t0 = time.perf_counter()
        resp = client.models.generate_content(model=model_name, contents=contents, config=config)
        elapsed = time.perf_counter() - t0
        content = resp.text or ''
        usage = resp.usage_metadata
        tokens_in = usage.prompt_token_count if usage else 0
        tokens_out = usage.candidates_token_count if usage else 0
        cost = _estimate_cost(model_name, tokens_in, tokens_out)
        return AIResponse(content=content.strip(), tokens_in=tokens_in, tokens_out=tokens_out,
                          cost_usd=cost, response_time_s=round(elapsed, 3), refused=False, model=model_name, raw=resp)

    def _call_anthropic(self, messages: list[dict[str, str]], model_config: dict[str, str],
                        *, temperature: float | None = None, max_tokens: int = 4096) -> AIResponse:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        model_name = model_config['name']
        system_text = self._extract_system(messages)
        api_messages = [m for m in messages if m['role'] != 'system']
        temp = 0.2 if temperature is None else temperature
        t0 = time.perf_counter()
        resp = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=temp,
            system=system_text,
            messages=api_messages)
        elapsed = time.perf_counter() - t0
        content = resp.content[0].text if resp.content else ''
        tokens_in = resp.usage.input_tokens
        tokens_out = resp.usage.output_tokens
        cost = _estimate_cost(model_name, tokens_in, tokens_out)
        return AIResponse(content=content.strip(), tokens_in=tokens_in, tokens_out=tokens_out,
                          cost_usd=cost, response_time_s=round(elapsed, 3), refused=False, model=model_name, raw=resp)

    @staticmethod
    def _extract_system(messages: list[dict[str, str]]) -> str:
        parts = [m['content'] for m in messages if m['role'] == 'system']
        return '\n\n'.join(parts)

    @staticmethod
    def _to_gemini_contents(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
        contents: list[dict[str, Any]] = []
        for m in messages:
            if m['role'] == 'system':
                continue
            role = 'model' if m['role'] == 'assistant' else 'user'
            contents.append({'role': role, 'parts': [{'text': m['content']}]})
        return contents
