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
from research_copilot.schemas import AuditReport


@dataclass(frozen=True)
class CopilotInput:
    paper: str | Path
    repo: str | Path
    benchmark: str
    model_card: str | Path | None = None
    reviews: str | Path | None = None
    use_retrieval: bool = True


def build_audit(inputs: CopilotInput) -> AuditReport:
    paper = load_paper(inputs.paper)
    model_card_text = load_model_card(inputs.model_card)
    reviews_text = load_reviews(inputs.reviews)
    repo = load_repo(inputs.repo)

    code_index = build_index(repo) if inputs.use_retrieval else None

    supplementary = "\n\n".join(s for s in (model_card_text, reviews_text) if s)

    claims = extract_claims(paper)
    missing = detect_missing_details(paper, supplementary)
    repo_signals = enrich_repo_signals(repo)

    return audit_claims(
        benchmark=inputs.benchmark,
        paper_title=paper.metadata.get("title"),
        paper_id=paper.metadata.get("arxiv_id"),
        claims=claims,
        overall_missing=missing,
        repo=repo,
        repo_signals=repo_signals,
        code_index=code_index,
    )
