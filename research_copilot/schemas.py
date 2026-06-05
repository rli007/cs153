"""Pydantic models that define the audit pipeline's data shapes.

These models are also the single source of truth for prompt schemas: each
extraction/audit step asks the LLM to produce JSON matching a snippet generated
from one of these classes via :func:`schema_for`.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


_StrictModel = ConfigDict(extra="ignore")


class EvidenceSpan(BaseModel):
    model_config = _StrictModel

    quote: str = Field(description="A short verbatim quote from the source document.")
    location: str | None = Field(
        default=None,
        description="Coarse location, e.g. 'Abstract', 'Section 3.2', 'Table 1', 'p. 4'.",
    )


class Metric(BaseModel):
    model_config = _StrictModel

    name: str = Field(description="Metric name, e.g. 'macro F1', 'top-1 accuracy', 'BLEU'.")
    baseline_value: float | None = None
    proposed_value: float | None = None
    delta: float | None = None
    units: str | None = None


class DatasetRef(BaseModel):
    model_config = _StrictModel

    name: str
    split: str | None = None
    size: str | None = None


class Claim(BaseModel):
    model_config = _StrictModel

    statement: str = Field(description="The empirical claim, paraphrased into a single sentence.")
    metric: Metric | None = None
    dataset: DatasetRef | None = None
    baseline_name: str | None = None
    method_name: str | None = None
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    is_main_claim: bool = False


MissingCategory = Literal[
    "random_seed",
    "hardware",
    "data_split",
    "hyperparameters",
    "checkpoint",
    "evaluation_script",
    "data_preprocessing",
    "training_recipe",
    "license",
    "compute_budget",
    "model_architecture",
    "dataset_details",
    "code_availability",
    "dependencies",
    "other",
]


_MISSING_CATEGORY_VALUES = {
    "random_seed",
    "hardware",
    "data_split",
    "hyperparameters",
    "checkpoint",
    "evaluation_script",
    "data_preprocessing",
    "training_recipe",
    "license",
    "compute_budget",
    "model_architecture",
    "dataset_details",
    "code_availability",
    "dependencies",
    "other",
}


def coerce_missing_category(value: object) -> str:
    """Map any string to a known MissingCategory, falling back to ``other``."""
    if not isinstance(value, str):
        return "other"
    v = value.lower().strip().replace("-", "_").replace(" ", "_")
    if v in _MISSING_CATEGORY_VALUES:
        return v
    aliases = {
        "seed": "random_seed",
        "seeds": "random_seed",
        "compute": "compute_budget",
        "gpu": "hardware",
        "splits": "data_split",
        "hp": "hyperparameters",
        "ckpt": "checkpoint",
        "weights": "checkpoint",
        "eval": "evaluation_script",
        "metric": "evaluation_script",
        "preprocessing": "data_preprocessing",
        "preprocess": "data_preprocessing",
        "training": "training_recipe",
        "recipe": "training_recipe",
        "architecture": "model_architecture",
        "model": "model_architecture",
        "dataset": "dataset_details",
        "data": "dataset_details",
        "code": "code_availability",
        "deps": "dependencies",
        "requirements": "dependencies",
    }
    return aliases.get(v, "other")


class MissingDetail(BaseModel):
    model_config = _StrictModel

    category: MissingCategory
    description: str
    severity: Literal["low", "medium", "high"]
    evidence: list[EvidenceSpan] = Field(default_factory=list)


class RepoSignals(BaseModel):
    model_config = _StrictModel

    path: str
    exists: bool
    important_files: list[str] = Field(default_factory=list)
    likely_entry_points: list[str] = Field(default_factory=list)
    likely_eval_scripts: list[str] = Field(default_factory=list)
    likely_config_files: list[str] = Field(default_factory=list)
    dependency_files: list[str] = Field(default_factory=list)
    has_tests: bool = False
    notes: list[str] = Field(default_factory=list)


class CodeLink(BaseModel):
    model_config = _StrictModel

    path: str = Field(description="Relative path inside the implementation repo.")
    role: str = Field(
        description="What this file plays for the claim, e.g. 'training entry', 'eval script', 'config', 'dataset loader'."
    )
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str


Feasibility = Literal["low", "medium", "high"]


class ClaimAudit(BaseModel):
    model_config = _StrictModel

    claim: Claim
    code_links: list[CodeLink] = Field(default_factory=list)
    missing: list[MissingDetail] = Field(default_factory=list)
    feasibility: Feasibility
    blockers: list[str] = Field(default_factory=list)
    notes: str | None = None


class AuditReport(BaseModel):
    model_config = _StrictModel

    title: str = "Reproducibility Audit"
    paper_title: str | None = None
    paper_id: str | None = None
    benchmark: str
    repo_summary: RepoSignals
    claims: list[ClaimAudit]
    overall_missing: list[MissingDetail] = Field(default_factory=list)
    overall_feasibility: Feasibility
    risks: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


def schema_for(model: type[BaseModel]) -> str:
    """Compact JSON-schema-ish hint for a Pydantic model, suitable for prompts."""

    return json.dumps(model.model_json_schema(), indent=2)
