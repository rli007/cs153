"""HuggingFace model-card / dataset-card raw fetch.

We deliberately avoid the ``huggingface_hub`` dependency: a single GET against
``huggingface.co/<repo>/raw/main/README.md`` is enough for public model cards
and avoids auth headaches. The result is plain Markdown text.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx

from research_copilot.config import PROJECT_ROOT


_HF_URL = re.compile(
    r"^(?:https?://)?huggingface\.co/("
    r"(?:datasets/)?[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+"
    r")(?:/.*)?$",
    re.IGNORECASE,
)
_CACHE_DIR = PROJECT_ROOT / ".cache" / "model_cards"


def looks_like_hf_url(value: str) -> bool:
    return bool(_HF_URL.match(value.strip()))


def _hf_repo(value: str) -> str:
    match = _HF_URL.match(value.strip())
    if not match:
        raise ValueError(f"Not a HuggingFace URL: {value!r}")
    return match.group(1)


def fetch_model_card(value: str, *, timeout: float = 15.0) -> str:
    """Fetch the README/model-card text for a HuggingFace model or dataset URL."""

    repo_path = _hf_repo(value)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _CACHE_DIR / (repo_path.replace("/", "__") + ".md")
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    branches = ("main", "master")
    last_error: Exception | None = None
    for branch in branches:
        url = f"https://huggingface.co/{repo_path}/raw/{branch}/README.md"
        try:
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            if response.status_code == 200:
                cache_path.write_text(response.text, encoding="utf-8")
                return response.text
            if response.status_code in (404, 401):
                last_error = RuntimeError(
                    f"HF README not found at {url} (status {response.status_code})"
                )
                continue
            response.raise_for_status()
        except httpx.HTTPError as exc:
            last_error = exc
            continue
    raise RuntimeError(f"Could not fetch HuggingFace model card for {value!r}: {last_error}")


def load_model_card(value: str | Path | None) -> str:
    """Load a model card from a local file path or a HuggingFace URL."""

    if value is None:
        return ""
    text_value = str(value)
    if looks_like_hf_url(text_value):
        return fetch_model_card(text_value)
    path = Path(text_value)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return text_value
