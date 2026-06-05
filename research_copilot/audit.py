"""Per-claim audit: link claims to code, score feasibility, list blockers.

This is the central reasoning step. We feed the model:
- the structured list of claims (from ``extract.claims``)
- per-claim retrieved code chunks (from ``retrieve.code_search``) when an
  index is available, else just the repo signals + tree listing
- the structured list of paper-level missing details (from ``extract.missing``)
- the enriched repo signals (from ``extract.repo``)

and ask it to produce, for each claim, candidate code links inside the repo,
the subset of missing details that block THAT claim, an overall feasibility
label, and a short list of blockers. We also ask for an aggregate
``overall_feasibility``, ``risks``, and ``next_steps`` for the report header.
"""

from __future__ import annotations

from pydantic import ValidationError

from research_copilot.ingest import RepoFiles
from research_copilot.llm import complete_json
from research_copilot.retrieve import CodeIndex, search_for_claim
from research_copilot.schemas import (
    AuditReport,
    Claim,
    ClaimAudit,
    MissingDetail,
    RepoSignals,
    coerce_missing_category,
)


_SYSTEM = """\
You are a senior reproducibility engineer. For each empirical claim from a
paper, decide:

Assume the user is a competent SWE/research implementer: they can search the
web, install dependencies, read linked docs, download public models/datasets,
use hosted APIs, run local/remote models, and write reasonable glue code. Do
not downgrade feasibility solely because a model, dataset, checkpoint, or
hardware setup is not bundled inside the implementation repo. Treat those as
normal sourcing/configuration tasks unless the artifact is clearly private,
proprietary, unreleased, unnamed, or essential to exact historical numbers.
Before adding a blocker, ask whether a skilled implementer could likely source
the named artifact online (dataset hubs, model APIs, Hugging Face, GitHub,
Papers With Code, project pages) or use a documented substitute. If yes, put it
in notes/next_steps as a sourcing task rather than a blocker.

1. Which files in the implementation repo would most likely produce that claim
   (training entry, eval script, configs, dataset loader). Use ONLY files
   present in the provided file listing or in the per-claim retrieved chunks.
   Cite each link with a short rationale and a confidence in [0, 1]. Prefer
   chunk-supported links over filename-only guesses, but you may include
   filename-only links with lower confidence when no good chunk is retrieved.
2. Which paper-level missing details are blockers for THIS claim specifically.
   You may copy items from the supplied list of overall missing details, or
   add new claim-specific ones using the same schema.
3. Feasibility for an independent reproduction with the given repo + paper:
   - "high": clear entry point, eval script, configs, no high-severity gaps.
   - "medium": some pieces exist, one or two important gaps remain, or exact
     reproduction needs careful sourcing/substitution.
   - "low": no executable evidence, missing metric/eval definition, private
     unavailable artifacts, or an underspecified method that cannot be
     reasonably reconstructed.
4. A short list of blockers (free-text strings) and optional notes. Blockers
   should be reserved for private/undisclosed/unnamed/metric-defining details.
   Public datasets, model families, APIs, and ordinary eval scripts should be
   described as next steps unless exact historical replication truly requires
   author-only access.

Then give an aggregate verdict: ``overall_feasibility``, ``risks`` (cross-
cutting concerns), and ``next_steps`` (concrete things a human should do).
Risks should distinguish exact paper-number reproduction from practical
implementation of the method.

Return strict JSON. Do NOT invent file paths.
"""


_SCHEMA_HINT = (
    "A JSON object with shape: {"
    '"claim_audits": [{'
    '"claim_index": int, '
    '"code_links": [{"path": str, "role": str, "confidence": number, "rationale": str}], '
    '"missing": [{"category": str, "description": str, "severity": "low"|"medium"|"high", '
    '"evidence": [{"quote": str, "location"?: str}]}], '
    '"feasibility": "low"|"medium"|"high", '
    '"blockers": [str], '
    '"notes": str | null}], '
    '"overall_feasibility": "low"|"medium"|"high", '
    '"risks": [str], '
    '"next_steps": [str]'
    "}"
)


def _claim_brief(idx: int, claim: Claim) -> str:
    parts = [f"[{idx}] {claim.statement}"]
    if claim.metric:
        m = claim.metric
        parts.append(
            f"   metric={m.name}, baseline={m.baseline_value}, proposed={m.proposed_value}, delta={m.delta}"
        )
    if claim.dataset:
        parts.append(f"   dataset={claim.dataset.name} split={claim.dataset.split}")
    if claim.method_name or claim.baseline_name:
        parts.append(f"   method={claim.method_name} vs baseline={claim.baseline_name}")
    if claim.is_main_claim:
        parts.append("   (MAIN CLAIM)")
    return "\n".join(parts)


def _missing_brief(items: list[MissingDetail]) -> str:
    return "\n".join(f"- [{m.severity}] {m.category}: {m.description}" for m in items)


def _retrieved_block(
    idx: int,
    claim: Claim,
    code_index: CodeIndex | None,
    *,
    k: int = 6,
    chars_per_chunk: int = 500,
) -> str:
    if code_index is None or code_index.is_empty:
        return ""
    hits = search_for_claim(code_index, claim, k=k)
    if not hits:
        return ""
    lines = [f"Retrieved code chunks for claim [{idx}]:"]
    for chunk, score in hits:
        snippet = chunk.text
        if len(snippet) > chars_per_chunk:
            snippet = snippet[: chars_per_chunk - 3] + "..."
        lines.append(
            f"  ({score:.2f}) {chunk.path}:{chunk.start_line}-{chunk.end_line}\n"
            f"  ----\n  {snippet}\n  ----"
        )
    return "\n".join(lines)


def audit_claims(
    *,
    benchmark: str,
    paper_title: str | None,
    paper_id: str | None,
    paper_authors: list[str] | None = None,
    claims: list[Claim],
    overall_missing: list[MissingDetail],
    repo: RepoFiles,
    repo_signals: RepoSignals,
    code_index: CodeIndex | None = None,
) -> AuditReport:
    if not claims:
        return AuditReport(
            benchmark=benchmark,
            paper_title=paper_title,
            paper_id=paper_id,
            paper_authors=paper_authors or [],
            repo_summary=repo_signals,
            claims=[],
            overall_missing=overall_missing,
            overall_feasibility="low",
            risks=["No empirical claims were extracted from the paper."],
            next_steps=["Verify the paper text was ingested correctly and rerun extraction."],
        )

    claims_block = "\n\n".join(_claim_brief(i, c) for i, c in enumerate(claims))
    retrieved_blocks: list[str] = []
    for i, claim in enumerate(claims):
        block = _retrieved_block(i, claim, code_index)
        if block:
            retrieved_blocks.append(block)
    retrieved_section = "\n\n".join(retrieved_blocks) or "(retrieval index empty or unavailable)"

    missing_block = _missing_brief(overall_missing) or "(none reported)"
    tree_block = repo.tree_listing[:6000]
    files_summary = (
        f"important_files={repo_signals.important_files}\n"
        f"likely_entry_points={repo_signals.likely_entry_points}\n"
        f"likely_eval_scripts={repo_signals.likely_eval_scripts}\n"
        f"likely_config_files={repo_signals.likely_config_files}\n"
        f"dependency_files={repo_signals.dependency_files}\n"
        f"has_tests={repo_signals.has_tests}\n"
        f"notes={repo_signals.notes}"
    )

    user = (
        f"Benchmark target the user wants to reproduce: {benchmark}\n"
        f"Paper title: {paper_title or '(unknown)'}\n"
        f"Paper id: {paper_id or '(none)'}\n\n"
        f"Empirical claims:\n{claims_block}\n\n"
        f"Paper-level missing details (overall):\n{missing_block}\n\n"
        f"Repo signals:\n{files_summary}\n\n"
        f"Repo file listing (truncated):\n{tree_block}\n\n"
        f"Per-claim retrieved code chunks:\n{retrieved_section}\n\n"
        "Produce the JSON object specified by the schema. ``claim_audits`` "
        "must contain exactly one entry per claim, in the same order, with "
        "``claim_index`` matching the input index."
    )

    raw, _resp = complete_json(
        role="reason",
        system=_SYSTEM,
        user=user,
        schema_hint=_SCHEMA_HINT,
        max_tokens=16384,
    )

    if isinstance(raw, list):
        raw = {"claim_audits": raw}
    if not isinstance(raw, dict):
        raise ValueError(f"Audit step expected a JSON object, got {type(raw).__name__}")

    claim_audits_raw = raw.get("claim_audits") or []
    by_index: dict[int, dict] = {}
    for entry in claim_audits_raw:
        if not isinstance(entry, dict):
            continue
        idx = entry.get("claim_index")
        if isinstance(idx, int) and 0 <= idx < len(claims):
            by_index[idx] = entry

    claim_audits: list[ClaimAudit] = []
    for i, claim in enumerate(claims):
        entry = by_index.get(i, {})
        clean_missing = []
        for m in entry.get("missing", []) or []:
            if isinstance(m, dict):
                m = dict(m)
                m["category"] = coerce_missing_category(m.get("category"))
                clean_missing.append(m)
        try:
            audit = ClaimAudit.model_validate(
                {
                    "claim": claim.model_dump(),
                    "code_links": entry.get("code_links", []),
                    "missing": clean_missing,
                    "feasibility": entry.get("feasibility", "low"),
                    "blockers": entry.get("blockers", []),
                    "notes": entry.get("notes"),
                }
            )
        except ValidationError as exc:
            audit = ClaimAudit(
                claim=claim,
                feasibility="low",
                blockers=[f"audit step returned an invalid entry: {exc.error_count()} errors"],
            )
        claim_audits.append(audit)

    overall_feasibility = raw.get("overall_feasibility", "low")
    if overall_feasibility not in {"low", "medium", "high"}:
        overall_feasibility = "low"

    return AuditReport(
        benchmark=benchmark,
        paper_title=paper_title,
        paper_id=paper_id,
        paper_authors=paper_authors or [],
        repo_summary=repo_signals,
        claims=claim_audits,
        overall_missing=overall_missing,
        overall_feasibility=overall_feasibility,
        risks=[r for r in raw.get("risks", []) if isinstance(r, str)],
        next_steps=[s for s in raw.get("next_steps", []) if isinstance(s, str)],
    )
