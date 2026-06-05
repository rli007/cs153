"""Serialize an :class:`AuditReport` to Markdown or JSON."""

from __future__ import annotations

import json
from pathlib import Path

from research_copilot.schemas import AuditReport, ClaimAudit, MissingDetail


def write_json(report: AuditReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")


def _format_missing(items: list[MissingDetail]) -> list[str]:
    if not items:
        return ["- (none reported)"]
    return [f"- **[{m.severity}] {m.category}** \u2014 {m.description}" for m in items]


def _format_claim_audit(idx: int, audit: ClaimAudit) -> list[str]:
    claim = audit.claim
    lines: list[str] = []
    header = f"### Claim {idx + 1}"
    if claim.is_main_claim:
        header += " \u2014 _main claim_"
    lines.append(header)
    lines.append("")
    lines.append(f"> {claim.statement}")
    lines.append("")

    if claim.metric:
        m = claim.metric
        bits = [f"**Metric:** {m.name}"]
        if m.baseline_value is not None:
            bits.append(f"baseline {m.baseline_value}")
        if m.proposed_value is not None:
            bits.append(f"proposed {m.proposed_value}")
        if m.delta is not None:
            bits.append(f"delta {m.delta}")
        lines.append(" \u00b7 ".join(bits))
    if claim.dataset:
        lines.append(
            f"**Dataset:** {claim.dataset.name}"
            + (f" (split: {claim.dataset.split})" if claim.dataset.split else "")
        )
    if claim.method_name or claim.baseline_name:
        lines.append(
            f"**Method:** {claim.method_name or '?'} vs **Baseline:** {claim.baseline_name or '?'}"
        )
    lines.append(f"**Feasibility:** `{audit.feasibility}`")
    lines.append("")

    if claim.evidence:
        lines.append("**Evidence:**")
        for ev in claim.evidence:
            loc = f" _({ev.location})_" if ev.location else ""
            lines.append(f"> {ev.quote}{loc}")
        lines.append("")

    lines.append("**Code links:**")
    if audit.code_links:
        for link in audit.code_links:
            lines.append(
                f"- `{link.path}` \u2014 {link.role} (confidence {link.confidence:.2f}): {link.rationale}"
            )
    else:
        lines.append("- (no candidate code links identified)")
    lines.append("")

    if audit.missing:
        lines.append("**Missing for this claim:**")
        lines.extend(_format_missing(audit.missing))
        lines.append("")

    if audit.blockers:
        lines.append("**Blockers:**")
        for b in audit.blockers:
            lines.append(f"- {b}")
        lines.append("")

    if audit.notes:
        lines.append(f"**Notes:** {audit.notes}")
        lines.append("")

    return lines


def write_markdown(report: AuditReport, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append(f"# {report.title}")
    lines.append("")
    if report.paper_title:
        lines.append(f"**Paper:** {report.paper_title}")
    if report.paper_id:
        lines.append(f"**Paper id:** `{report.paper_id}`")
    if report.paper_authors:
        lines.append(f"**Authors:** {', '.join(report.paper_authors)}")
    lines.append(f"**Benchmark target:** {report.benchmark}")
    lines.append(f"**Overall feasibility:** `{report.overall_feasibility}`")
    lines.append("")

    lines.append("## Repository")
    lines.append("")
    rs = report.repo_summary
    lines.append(f"- Path: `{rs.path}`")
    lines.append(
        f"- Important files: {', '.join(rs.important_files) if rs.important_files else 'none detected'}"
    )
    lines.append(
        f"- Likely entry points: {', '.join(rs.likely_entry_points) if rs.likely_entry_points else 'none detected'}"
    )
    lines.append(
        f"- Likely eval scripts: {', '.join(rs.likely_eval_scripts) if rs.likely_eval_scripts else 'none detected'}"
    )
    lines.append(
        f"- Likely config files: {', '.join(rs.likely_config_files) if rs.likely_config_files else 'none detected'}"
    )
    lines.append(
        f"- Dependency files: {', '.join(rs.dependency_files) if rs.dependency_files else 'none detected'}"
    )
    lines.append(f"- Has tests: {rs.has_tests}")
    if rs.notes:
        lines.append("- Notes:")
        lines.extend(f"  - {n}" for n in rs.notes)
    lines.append("")

    lines.append("## Overall Missing Details")
    lines.append("")
    lines.extend(_format_missing(report.overall_missing))
    lines.append("")

    lines.append("## Claims Audit")
    lines.append("")
    if not report.claims:
        lines.append("(no claims extracted)")
        lines.append("")
    for i, audit in enumerate(report.claims):
        lines.extend(_format_claim_audit(i, audit))

    lines.append("## Risks")
    lines.append("")
    if report.risks:
        for r in report.risks:
            lines.append(f"- {r}")
    else:
        lines.append("- (none recorded)")
    lines.append("")

    lines.append("## Next Steps")
    lines.append("")
    if report.next_steps:
        for i, step in enumerate(report.next_steps, start=1):
            lines.append(f"{i}. {step}")
    else:
        lines.append("- (none recorded)")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
