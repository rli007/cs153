"""LLM-backed detection of missing reproducibility details."""

from __future__ import annotations

import json

from pydantic import TypeAdapter, ValidationError

from research_copilot.ingest import PaperText
from research_copilot.llm import complete_json
from research_copilot.schemas import MissingDetail, coerce_missing_category


_MISSING_ADAPTER = TypeAdapter(list[MissingDetail])

_MAX_PAPER_CHARS = 120_000

_SYSTEM = """\
You are a reproducibility-focused reviewer. Given a paper (and optional model
card), enumerate the implementation details that are MISSING or UNDERSPECIFIED
and would block an independent researcher from reproducing the headline
results.

Categories you may report (use these exact strings for ``category``):
random_seed, hardware, data_split, hyperparameters, checkpoint,
evaluation_script, data_preprocessing, training_recipe, license,
compute_budget, other.

Severity guide:
- high: cannot reproduce without it (e.g., undisclosed eval split, undisclosed
  proprietary checkpoint, no metric definition).
- medium: causes meaningful drift (e.g., no seed, no exact hyperparameters).
- low: nice-to-have (e.g., precise wall-clock, GPU model when CPU suffices).

Each missing detail should include a ``description`` that says specifically
what is missing, and ``evidence`` quotes (if any) from the paper text that
illustrate the gap (e.g., a sentence that mentions training but omits the
hyperparameters). It is OK to return zero evidence quotes if the gap is an
absence.

Do NOT report a category as missing if the paper or model card actually
provides the information.
"""

_SCHEMA_HINT = (
    'A JSON array of objects with shape: '
    '{"category": "random_seed"|"hardware"|"data_split"|"hyperparameters"|'
    '"checkpoint"|"evaluation_script"|"data_preprocessing"|"training_recipe"|'
    '"license"|"compute_budget"|"other", '
    '"description": str, '
    '"severity": "low"|"medium"|"high", '
    '"evidence": [{"quote": str, "location"?: str}]}'
)


def detect_missing_details(
    paper: PaperText, model_card_text: str = ""
) -> list[MissingDetail]:
    user_parts = [
        f"Paper source: {paper.source}",
        "Paper text (truncated):",
        "-----",
        paper.raw_text[:_MAX_PAPER_CHARS],
        "-----",
    ]
    if model_card_text:
        user_parts.extend([
            "",
            "Model card / supplementary text:",
            "-----",
            model_card_text[:20_000],
            "-----",
        ])
    user_parts.append("\nReturn a JSON array of missing-detail objects matching the schema.")

    raw, _resp = complete_json(
        role="extract",
        system=_SYSTEM,
        user="\n".join(user_parts),
        schema_hint=_SCHEMA_HINT,
        max_tokens=6144,
    )

    if isinstance(raw, dict) and "missing" in raw:
        raw = raw["missing"]
    if not isinstance(raw, list):
        raise ValueError(f"Expected list of missing details, got {type(raw).__name__}")

    cleaned_input: list[dict] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        item = dict(item)
        item["category"] = coerce_missing_category(item.get("category"))
        cleaned_input.append(item)

    try:
        return _MISSING_ADAPTER.validate_python(cleaned_input)
    except ValidationError as exc:
        cleaned: list[MissingDetail] = []
        for item in cleaned_input:
            try:
                cleaned.append(MissingDetail.model_validate(item))
            except ValidationError:
                continue
        if not cleaned and cleaned_input:
            raise ValueError(f"All missing-detail items failed validation: {exc}\nRaw: {json.dumps(raw)[:600]}")
        return cleaned
