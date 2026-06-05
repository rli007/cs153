"""LLM-backed empirical claim extraction.

Replaces the keyword-heuristic extractor in ``research_copilot.extractors``.
We send the (truncated) paper text to a long-context model and ask for a JSON
list of structured claims grounded in short verbatim quotes.
"""

from __future__ import annotations

import json

from pydantic import TypeAdapter, ValidationError

from research_copilot.ingest import PaperText
from research_copilot.llm import complete_json
from research_copilot.schemas import Claim


_CLAIMS_ADAPTER = TypeAdapter(list[Claim])

_MAX_PAPER_CHARS = 120_000


_SYSTEM = """\
You are a careful scientific reviewer. You read a research paper and extract
its empirical claims: statements of measurable performance backed by an
experiment in the paper. You must NOT invent metrics or numbers. Every claim
should be supported by a short verbatim quote from the paper.

Definition of an empirical claim:
- A statement that the proposed method achieves a specific quantitative result
  on a named dataset/benchmark, optionally compared to a baseline.
- Examples: "Our method reaches 78.4 macro F1 on AG-News, up from 71.2",
  "We reduce perplexity by 12% on WikiText-103".

Do NOT include:
- Opinions, motivations, or future-work claims.
- Pure qualitative statements with no metric.
- Claims attributed to other papers (cited results) unless the authors run them.

Pick at most 8 claims, prioritizing the main headline result first.
Set ``is_main_claim`` to true for at most ONE claim (the headline).
"""


_SCHEMA_HINT = (
    'A JSON array of objects with shape: '
    '{"statement": str, '
    '"metric": {"name": str, "baseline_value"?: number, "proposed_value"?: number, "delta"?: number, "units"?: str} | null, '
    '"dataset": {"name": str, "split"?: str, "size"?: str} | null, '
    '"baseline_name"?: str | null, '
    '"method_name"?: str | null, '
    '"evidence": [{"quote": str, "location"?: str}], '
    '"is_main_claim": bool}'
)


def extract_claims(paper: PaperText) -> list[Claim]:
    """Return a list of empirical claims grounded by short verbatim quotes."""

    snippet = paper.raw_text[:_MAX_PAPER_CHARS]
    user = (
        f"Paper source: {paper.source}\n"
        f"Paper text (truncated to {_MAX_PAPER_CHARS} chars):\n"
        "-----\n"
        f"{snippet}\n"
        "-----\n\n"
        "Return a JSON array of empirical-claim objects matching the schema."
    )

    raw, _resp = complete_json(
        role="extract",
        system=_SYSTEM,
        user=user,
        schema_hint=_SCHEMA_HINT,
        max_tokens=4096,
    )

    if not isinstance(raw, list):
        if isinstance(raw, dict) and "claims" in raw and isinstance(raw["claims"], list):
            raw = raw["claims"]
        else:
            raise ValueError(f"Expected a JSON array of claims, got: {type(raw).__name__}")

    try:
        return _CLAIMS_ADAPTER.validate_python(raw)
    except ValidationError as exc:
        cleaned: list[Claim] = []
        for item in raw:
            try:
                cleaned.append(Claim.model_validate(item))
            except ValidationError:
                continue
        if not cleaned:
            raise ValueError(f"All claims failed validation: {exc}\nRaw: {json.dumps(raw)[:600]}")
        return cleaned
