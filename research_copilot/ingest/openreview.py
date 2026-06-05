"""OpenReview reviews ingest via the public API v2.

Accepts a forum URL, an ``?id=...`` URL, or a bare note id. Returns the
review/meta-review text concatenated into a single string suitable for
feeding into ``detect_missing_details`` as supplementary signal. Reviewer
concerns are an excellent source of "missing detail" labels.

We use the unauthenticated public API which works for accepted submissions at
ICLR / NeurIPS / etc. Some venues hide reviews; in that case we return an
empty string and surface a warning via the caller.
"""

from __future__ import annotations

import re
from pathlib import Path

import httpx

from research_copilot.config import PROJECT_ROOT


_OPENREVIEW_FORUM = re.compile(
    r"openreview\.net/(?:forum|pdf)\?id=([A-Za-z0-9_-]+)",
    re.IGNORECASE,
)
_OPENREVIEW_NOTE = re.compile(r"openreview\.net/notes\?id=([A-Za-z0-9_-]+)", re.IGNORECASE)
_BARE_ID = re.compile(r"^[A-Za-z0-9_-]{6,}$")

_API_BASE = "https://api2.openreview.net"
_CACHE_DIR = PROJECT_ROOT / ".cache" / "openreview"


def looks_like_openreview(value: str) -> bool:
    if "openreview.net" in value.lower():
        return True
    return bool(_BARE_ID.fullmatch(value.strip())) and not value.strip().isdigit()


def _forum_id(value: str) -> str:
    text = value.strip()
    for pattern in (_OPENREVIEW_FORUM, _OPENREVIEW_NOTE):
        match = pattern.search(text)
        if match:
            return match.group(1)
    if _BARE_ID.fullmatch(text):
        return text
    raise ValueError(f"Could not parse an OpenReview id from {value!r}")


def _value_of(field: object) -> str | None:
    if isinstance(field, dict):
        for key in ("value", "values"):
            if key in field:
                inner = field[key]
                if isinstance(inner, list):
                    return "\n".join(str(x) for x in inner)
                return str(inner)
    if isinstance(field, str):
        return field
    return None


def _format_note(note: dict) -> str:
    invitation = note.get("invitations") or [note.get("invitation", "")]
    invitation_str = ", ".join(invitation) if isinstance(invitation, list) else str(invitation)
    content = note.get("content") or {}
    parts = [f"--- Note ({invitation_str}) ---"]
    for field in (
        "title",
        "summary",
        "strengths",
        "weaknesses",
        "questions",
        "limitations",
        "soundness",
        "presentation",
        "contribution",
        "rating",
        "confidence",
        "review",
        "comment",
        "decision",
        "metareview",
    ):
        if field in content:
            value = _value_of(content[field])
            if value:
                parts.append(f"{field.upper()}: {value}")
    return "\n".join(parts)


def fetch_reviews(value: str, *, timeout: float = 20.0) -> str:
    forum = _forum_id(value)
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = _CACHE_DIR / f"{forum}.md"
    if cache_path.exists():
        return cache_path.read_text(encoding="utf-8")

    url = f"{_API_BASE}/notes"
    params = {"forum": forum, "details": "replyCount"}
    try:
        response = httpx.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"OpenReview fetch failed for {forum!r}: {exc}") from exc

    notes = data.get("notes", [])
    if not notes:
        return ""

    blocks: list[str] = []
    for note in notes:
        formatted = _format_note(note)
        if formatted.count("\n") > 0:
            blocks.append(formatted)

    text = "\n\n".join(blocks)
    cache_path.write_text(text, encoding="utf-8")
    return text


def load_reviews(value: str | Path | None) -> str:
    if value is None:
        return ""
    text_value = str(value)
    if looks_like_openreview(text_value):
        try:
            return fetch_reviews(text_value)
        except RuntimeError:
            return ""
    path = Path(text_value)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
