"""OpenRouter free-tier LLM client.

Features:

- Speaks the OpenAI-compatible REST endpoint at ``https://openrouter.ai/api/v1``.
- Per-role model rotation; on rate-limit or transient errors, fall through to
  the next candidate model.
- Token-bucket rate limiter to stay under the 20 req/min free-tier cap.
- Disk cache keyed by ``sha256(model + system + user + schema_hint)`` so
  re-runs cost zero new calls.
- Best-effort JSON extraction with a single repair attempt on parse failure.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any

from openai import APIError, APIStatusError, OpenAI, RateLimitError

from research_copilot.config import (
    CACHE_DIR,
    DEFAULT_BASE_URL,
    MODEL_ROUTES,
    REQUESTS_PER_MINUTE,
    ensure_dirs,
    is_reasoning_model,
)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    cached: bool


class _TokenBucket:
    def __init__(self, rate_per_minute: int) -> None:
        self.capacity = float(rate_per_minute)
        self.tokens = float(rate_per_minute)
        self.refill_per_sec = rate_per_minute / 60.0
        self.last_refill = time.monotonic()

    def acquire(self) -> None:
        while True:
            now = time.monotonic()
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_sec)
            self.last_refill = now
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                return
            time.sleep((1.0 - self.tokens) / self.refill_per_sec + 0.05)


_BUCKET = _TokenBucket(REQUESTS_PER_MINUTE)
_CLIENT: OpenAI | None = None


def _client() -> OpenAI:
    global _CLIENT
    if _CLIENT is not None:
        return _CLIENT
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    base_url = os.environ.get("OPENROUTER_BASE_URL", DEFAULT_BASE_URL)
    _CLIENT = OpenAI(api_key=api_key, base_url=base_url)
    return _CLIENT


def _cache_key(model: str, system: str, user: str, schema_hint: str | None) -> str:
    h = hashlib.sha256()
    for part in (model, system, user, schema_hint or ""):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def _resolve_models(role_or_model: str) -> list[str]:
    if role_or_model in MODEL_ROUTES:
        return list(MODEL_ROUTES[role_or_model])
    return [role_or_model]


def complete(
    role: str,
    system: str,
    user: str,
    *,
    schema_hint: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    use_cache: bool = True,
) -> LLMResponse:
    """Run a chat completion using the model rotation for ``role``.

    Falls through to the next model on 429/5xx/transient errors. Caches the
    first successful response on disk.
    """

    ensure_dirs()
    candidates = _resolve_models(role)
    last_error: Exception | None = None
    client = _client()

    for model in candidates:
        key = _cache_key(model, system, user, schema_hint)
        cache_path = CACHE_DIR / f"{key}.json"

        if use_cache and cache_path.exists():
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            return LLMResponse(text=data["text"], model=data["model"], cached=True)

        try:
            _BUCKET.acquire()
            effective_max = max_tokens + 4096 if is_reasoning_model(model) else max_tokens
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": effective_max,
            }
            if not is_reasoning_model(model):
                kwargs["temperature"] = temperature
            response = client.chat.completions.create(**kwargs)
            text = response.choices[0].message.content or ""
            cache_path.write_text(
                json.dumps({"text": text, "model": model}, indent=2),
                encoding="utf-8",
            )
            return LLMResponse(text=text, model=model, cached=False)
        except RateLimitError as exc:
            last_error = exc
            continue
        except APIStatusError as exc:
            last_error = exc
            if exc.status_code in (404, 429, 500, 502, 503, 504):
                continue
            raise
        except APIError as exc:
            last_error = exc
            continue

    raise RuntimeError(
        f"All models in route '{role}' failed. Tried: {candidates}. Last error: {last_error}"
    )


_FENCE_OPEN = re.compile(r"```(?:json|JSON)?\s*", re.IGNORECASE)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences (greedy outer match)."""
    text = text.strip()
    m = _FENCE_OPEN.search(text)
    if m:
        text = text[m.end() :]
    if text.endswith("```"):
        text = text[: -3]
    return text.strip()


def _balance_truncated(text: str) -> str | None:
    """Best-effort recovery of a JSON value cut off by max_tokens.

    Walks the text and counts brace/bracket depth, ignoring chars inside strings.
    Trims trailing junk and appends any unclosed closers in reverse order.
    """
    if not text or text[0] not in "[{":
        return None
    stack: list[str] = []
    in_string = False
    escape = False
    last_complete = -1
    for i, ch in enumerate(text):
        if escape:
            escape = False
            continue
        if ch == "\\" and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]":
            if stack and stack[-1] == ch:
                stack.pop()
                if not stack:
                    last_complete = i
    if not stack:
        return None
    truncated = text[: last_complete + 1] if last_complete >= 0 else text
    if last_complete >= 0:
        return truncated
    while truncated and truncated[-1] in ", \n\r\t":
        truncated = truncated[:-1]
    if in_string:
        truncated += '"'
    return truncated + "".join(reversed(stack))


def extract_json(text: str) -> Any:
    """Pull a JSON value out of a possibly noisy / truncated model response."""

    cleaned = _strip_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    for opener, closer in (("{", "}"), ("[", "]")):
        start = cleaned.find(opener)
        end = cleaned.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                continue

    for opener in ("{", "["):
        start = cleaned.find(opener)
        if start == -1:
            continue
        repaired = _balance_truncated(cleaned[start:])
        if repaired:
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                continue

    raise ValueError(
        f"Could not extract JSON from response (first 400 chars):\n{text[:400]}"
    )


def complete_json(
    role: str,
    system: str,
    user: str,
    *,
    schema_hint: str,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    repair_attempts: int = 1,
) -> tuple[Any, LLMResponse]:
    """Run a completion and parse JSON, with optional repair attempts."""

    full_system = (
        f"{system}\n\n"
        "Return ONLY a single valid JSON value matching this schema. "
        "Do not include prose, explanations, or markdown fences.\n\n"
        f"Schema:\n{schema_hint}"
    )

    response = complete(
        role,
        full_system,
        user,
        schema_hint=schema_hint,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    try:
        return extract_json(response.text), response
    except ValueError as parse_err:
        if repair_attempts <= 0:
            raise

        repair_system = (
            "You are a strict JSON repair tool. Output ONLY a single valid JSON "
            "value matching the requested schema. No prose, no markdown."
        )
        repair_user = (
            f"Schema:\n{schema_hint}\n\n"
            f"Previous response (which failed to parse as JSON):\n{response.text}\n\n"
            f"Parse error: {parse_err}"
        )
        repair_response = complete(
            role,
            repair_system,
            repair_user,
            schema_hint=f"REPAIR::{schema_hint}",
            temperature=0.0,
            max_tokens=max_tokens,
            use_cache=False,
        )
        return extract_json(repair_response.text), repair_response
