"""Top-level orchestration for the reproducibility audit pipeline.

The flow:

1. Ingest the paper (text / pdf / arxiv) and the repo (local path or GitHub URL).
2. (Optional) Build a local embedding index over the repo's text/code chunks.
3. Ingest optional supplementary signals: HuggingFace model card, OpenReview reviews.
4. LLM call: extract structured empirical claims from the paper.
5. LLM call: detect missing reproducibility details from paper + model card + reviews.
6. LLM call: enrich the filesystem repo signals (entry points, eval, configs).
7. LLM call: audit each claim against the repo + retrieved code chunks.

Total cost: ~4 cold LLM calls when the cache is cold; 0 when the inputs are
unchanged. Embeddings run locally and are also disk-cached.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_copilot.audit import audit_claims
from research_copilot.extract import (
    detect_missing_details,
    enrich_repo_signals,
    extract_claims,
)
from research_copilot.ingest import (
    load_model_card,
    load_paper,
    load_repo,
    load_reviews,
)
from research_copilot.retrieve import build_index
from research_copilot.schemas import AuditReport, ClaimAudit, MissingDetail, RepoSignals


@dataclass(frozen=True)
class CopilotInput:
    paper: str | Path
    repo: str | Path | None
    benchmark: str
    model_card: str | Path | None = None
    reviews: str | Path | None = None
    use_retrieval: bool = True


def build_audit(inputs: CopilotInput) -> AuditReport:
    paper = load_paper(inputs.paper)
    model_card_text = load_model_card(inputs.model_card)
    reviews_text = load_reviews(inputs.reviews)

    supplementary = "\n\n".join(s for s in (model_card_text, reviews_text) if s)

    claims = extract_claims(paper)
    missing = detect_missing_details(paper, supplementary)

    if inputs.repo is None or not str(inputs.repo).strip():
        repo_missing = MissingDetail(
            category="code_availability",
            description=(
                "No implementation repository was supplied or discovered, so the system "
                "cannot link claims to code or propose runnable commands."
            ),
            severity="high",
            evidence=[],
        )
        repo_signals = RepoSignals(
            path="(none)",
            exists=False,
            notes=[
                "Repository discovery did not find a usable implementation.",
                "This report is limited to paper-only reproducibility triage.",
            ],
        )
        return AuditReport(
            benchmark=inputs.benchmark,
            paper_title=paper.metadata.get("title"),
            paper_id=paper.metadata.get("arxiv_id"),
            paper_authors=list(paper.metadata.get("authors") or []),
            repo_summary=repo_signals,
            claims=[
                ClaimAudit(
                    claim=claim,
                    feasibility="low",
                    missing=[repo_missing],
                    blockers=[
                        "No implementation repository is available for code-linking or execution planning."
                    ],
                    notes="Paper-only mode: claim extraction and missing-detail detection ran, but no repo audit was possible.",
                )
                for claim in claims
            ],
            overall_missing=[repo_missing] + missing,
            overall_feasibility="low",
            risks=[
                "No repository was available, so code availability is the primary blocker.",
                "Expected commands, dependency checks, and evaluation scripts cannot be verified.",
            ],
            next_steps=[
                "Search for an official repository from the paper page, author homepage, or GitHub.",
                "Ask the authors for the intended implementation repository and reproduction command.",
            ],
        )

    repo = load_repo(inputs.repo)
    code_index = build_index(repo) if inputs.use_retrieval else None
    repo_signals = enrich_repo_signals(repo)

    return audit_claims(
        benchmark=inputs.benchmark,
        paper_title=paper.metadata.get("title"),
        paper_id=paper.metadata.get("arxiv_id"),
        paper_authors=list(paper.metadata.get("authors") or []),
        claims=claims,
        overall_missing=missing,
        repo=repo,
        repo_signals=repo_signals,
        code_index=code_index,
    )
