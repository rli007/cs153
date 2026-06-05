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
        "meta-llama/llama-4-scout:free",
        "qwen/qwen3-coder:free",
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "extract": [
        "deepseek/deepseek-chat-v3-0324:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "qwen/qwen3-coder:free",
        "google/gemini-2.0-flash-exp:free",
    ],
    "code": [
        "qwen/qwen3-coder:free",
        "deepseek/deepseek-chat-v3-0324:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "reason": [
        "deepseek/deepseek-r1:free",
        "deepseek/deepseek-chat-v3-0324:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ],
    "triage": [
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-chat-v3-0324:free",
    ],
}


def ensure_dirs() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    PAPER_CACHE_DIR.mkdir(parents=True, exist_ok=True)
