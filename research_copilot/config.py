"""Configuration for the research copilot.

Reads OpenRouter credentials from the environment (or a local .env) and defines
the model rotation routes used by ``research_copilot.llm``.

The free OpenRouter tier rate-limits at 20 requests/minute and 1000 requests/day
(once $10+ in lifetime credits is on the account). Rotating across model IDs
effectively multiplies day-level capacity since limits are tracked per model.
The lists below should be edited as free-tier availability changes.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CACHE_DIR = Path(os.environ.get("RC_CACHE_DIR", PROJECT_ROOT / ".cache" / "llm"))
PAPER_CACHE_DIR = Path(
    os.environ.get("RC_PAPER_CACHE_DIR", PROJECT_ROOT / ".cache" / "papers")
)

REQUESTS_PER_MINUTE = int(os.environ.get("RC_RPM", "18"))


_STANDARD_MODEL_ROUTES: dict[str, list[str]] = {
    "long_ingest": [
        "google/gemini-2.5-flash-lite",
        "deepseek/deepseek-v4-flash",
        "qwen/qwen3-coder:free",
    ],
    "extract": [
        "google/gemini-2.5-flash-lite",
        "deepseek/deepseek-v4-flash",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "code": [
        "qwen/qwen3-coder-30b-a3b-instruct",
        "qwen/qwen3-coder:free",
        "google/gemini-2.5-flash-lite",
    ],
    "reason": [
        "google/gemini-2.5-flash",
        "deepseek/deepseek-v4-flash",
        "google/gemini-2.5-flash-lite",
    ],
    "triage": [
        "google/gemini-2.5-flash-lite",
        "deepseek/deepseek-v4-flash",
    ],
}


_PREMIUM_MODEL_ROUTES: dict[str, list[str]] = {
    "long_ingest": [
        "google/gemini-2.5-pro",
        "openai/gpt-5-mini",
        "google/gemini-2.5-flash",
    ],
    "extract": [
        "openai/gpt-5-mini",
        "google/gemini-2.5-pro",
        "anthropic/claude-sonnet-4.5",
        "google/gemini-2.5-flash",
    ],
    "code": [
        "openai/gpt-5-mini",
        "anthropic/claude-sonnet-4.5",
        "qwen/qwen3-coder-30b-a3b-instruct",
        "google/gemini-2.5-flash",
    ],
    "reason": [
        "openai/gpt-5.1",
        "openai/gpt-5",
        "anthropic/claude-sonnet-4.5",
        "google/gemini-2.5-pro",
    ],
    "triage": [
        "openai/gpt-5-mini",
        "google/gemini-2.5-pro",
        "google/gemini-2.5-flash",
    ],
}


def _truthy(value: str | None) -> bool:
    return value is not None and value.lower() not in {"0", "false", "no", "off"}


def _route_override(role: str, fallback: list[str]) -> list[str]:
    raw = os.environ.get(f"RC_{role.upper()}_MODELS")
    if not raw:
        return fallback
    models = [item.strip() for item in raw.split(",") if item.strip()]
    return models or fallback


USE_PREMIUM_MODELS = _truthy(os.environ.get("RC_PREMIUM_MODELS", "0"))
_BASE_ROUTES = _PREMIUM_MODEL_ROUTES if USE_PREMIUM_MODELS else _STANDARD_MODEL_ROUTES
MODEL_ROUTES: dict[str, list[str]] = {
    role: _route_override(role, models)
    for role, models in _BASE_ROUTES.items()
}


REASONING_MODELS: set[str] = {
    "openai/gpt-5-nano",
    "openai/gpt-5-mini",
    "openai/gpt-5",
    "openai/gpt-5.1",
    "openai/gpt-5.4-mini",
    "openai/gpt-5.4-nano",
    "qwen/qwen3-next-80b-a3b-thinking",
    "qwen/qwen3-235b-a22b-thinking-2507",
    "deepseek/deepseek-r1",
    "deepseek/deepseek-r1-0528",
}


def is_reasoning_model(model_id: str) -> bool:
    return model_id in REASONING_MODELS


def ensure_dirs() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
