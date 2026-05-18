from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from research_copilot.extractors import extract_claims, identify_missing_details, read_text
from research_copilot.repo_inspector import inspect_repo


@dataclass(frozen=True)
class CopilotInput:
    paper_path: Path
    repo_path: Path
    benchmark: str
    model_card_path: Path | None = None


@dataclass(frozen=True)
class ReproductionPlan:
    title: str
    benchmark: str
    claims: list[str]
    missing_details: list[str]
    repo_summary: dict[str, object]
    experiment_steps: list[str]
    generated_artifacts: list[str]
    risks: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_reproduction_plan(inputs: CopilotInput) -> ReproductionPlan:
    paper_text = read_text(inputs.paper_path)
    model_card_text = read_text(inputs.model_card_path) if inputs.model_card_path else ""
    repo_summary = inspect_repo(inputs.repo_path)
    claims = extract_claims(paper_text)
    missing_details = identify_missing_details(paper_text, model_card_text)

    return ReproductionPlan(
        title="Research Artifact to Reproducible Workflow Plan",
        benchmark=inputs.benchmark,
        claims=claims,
        missing_details=missing_details,
        repo_summary=repo_summary,
        experiment_steps=[
            "Confirm the target claim and metric definition.",
            "Map repository entry points to training, inference, and evaluation commands.",
            "Create a minimal environment file and smoke-test command.",
            "Run a small-scale reproduction pass before attempting the full benchmark.",
            "Compare observed metrics against the paper claim and record gaps.",
        ],
        generated_artifacts=[
            "reproduction_plan.md",
            "future: experiment config",
            "future: run script",
            "future: evaluation report",
        ],
        risks=[
            "Paper text parsing is currently plain-text only.",
            "Claim extraction uses heuristics and should be replaced with structured LLM extraction.",
            "Experiment execution is planned but not yet automated.",
        ],
    )
