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


MODEL_ROUTES: dict[str, list[str]] = {
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
