"""Run an audit against every paper in a bench spec and aggregate scores."""

from __future__ import annotations

import json
import statistics
from dataclasses import asdict, dataclass, field
from pathlib import Path

from research_copilot.eval.rubric import (
    BenchSpec,
    PaperEntry,
    PaperScore,
    load_bench_spec,
    score_audit,
)
from research_copilot.workflow import CopilotInput, build_audit
from research_copilot.writers import write_json, write_markdown


@dataclass
class BenchResult:
    spec_name: str
    spec_description: str
    paper_scores: list[PaperScore]
    aggregate_claim_coverage: float
    aggregate_gap_f1: float
    aggregate_link_accuracy: float
    feasibility_pass_rate: float
    aggregate_score: float
    failed: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "spec_name": self.spec_name,
            "spec_description": self.spec_description,
            "aggregate": {
                "claim_coverage": self.aggregate_claim_coverage,
                "gap_f1": self.aggregate_gap_f1,
                "link_accuracy": self.aggregate_link_accuracy,
                "feasibility_pass_rate": self.feasibility_pass_rate,
                "overall": self.aggregate_score,
            },
            "papers": [
                {
                    "paper_id": ps.paper_id,
                    "rubric": asdict(ps.rubric),
                    "notes": ps.notes,
                }
                for ps in self.paper_scores
            ],
            "failed": self.failed,
        }


def _run_one(
    entry: PaperEntry,
    output_dir: Path,
    use_retrieval: bool = True,
) -> tuple[PaperScore | None, dict | None]:
    try:
        report = build_audit(
            CopilotInput(
                paper=entry.paper,
                repo=entry.repo,
                benchmark=entry.benchmark,
                model_card=entry.model_card,
                reviews=entry.reviews,
                use_retrieval=use_retrieval,
            )
        )
    except Exception as exc:
        return None, {"paper_id": entry.id, "error": f"{type(exc).__name__}: {exc}"}

    paper_dir = output_dir / entry.id
    paper_dir.mkdir(parents=True, exist_ok=True)
    write_markdown(report, paper_dir / "audit.md")
    write_json(report, paper_dir / "audit.json")

    score = score_audit(report, entry.ground_truth)
    score.paper_id = entry.id
    return score, None


def _mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else 0.0


def run_bench(
    spec: BenchSpec,
    output_dir: Path,
    use_retrieval: bool = True,
) -> BenchResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    scores: list[PaperScore] = []
    failed: list[dict] = []
    for entry in spec.papers:
        score, error = _run_one(entry, output_dir, use_retrieval=use_retrieval)
        if error is not None:
            failed.append(error)
            continue
        if score is not None:
            scores.append(score)

    coverage = _mean([s.rubric.claim_coverage for s in scores])
    gap_f1 = _mean([s.rubric.gap_f1 for s in scores])
    link = _mean([s.rubric.link_accuracy for s in scores])
    feas = _mean([1.0 if s.rubric.feasibility_pass else 0.0 for s in scores])
    overall = _mean([s.rubric.aggregate() for s in scores])

    result = BenchResult(
        spec_name=spec.name,
        spec_description=spec.description,
        paper_scores=scores,
        aggregate_claim_coverage=coverage,
        aggregate_gap_f1=gap_f1,
        aggregate_link_accuracy=link,
        feasibility_pass_rate=feas,
        aggregate_score=overall,
        failed=failed,
    )

    summary_path = output_dir / "bench_summary.json"
    summary_path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    md_lines: list[str] = []
    md_lines.append(f"# Bench: {result.spec_name}")
    md_lines.append("")
    if result.spec_description:
        md_lines.append(result.spec_description)
        md_lines.append("")
    md_lines.append("## Aggregate")
    md_lines.append("")
    md_lines.append(f"- claim_coverage: {coverage:.3f}")
    md_lines.append(f"- gap_f1: {gap_f1:.3f}")
    md_lines.append(f"- link_accuracy: {link:.3f}")
    md_lines.append(f"- feasibility_pass_rate: {feas:.3f}")
    md_lines.append(f"- overall: {overall:.3f}")
    md_lines.append("")
    md_lines.append("## Per-paper")
    md_lines.append("")
    for ps in result.paper_scores:
        md_lines.append(f"### {ps.paper_id}")
        r = ps.rubric
        md_lines.append(
            f"- claim_coverage={r.claim_coverage:.3f} \u00b7 gap_f1={r.gap_f1:.3f} "
            f"\u00b7 link_accuracy={r.link_accuracy:.3f} "
            f"\u00b7 feasibility_pass={r.feasibility_pass} "
            f"\u00b7 aggregate={r.aggregate():.3f}"
        )
        if ps.notes:
            md_lines.append("- notes:")
            md_lines.extend(f"  - {n}" for n in ps.notes)
        md_lines.append("")
    if result.failed:
        md_lines.append("## Failures")
        md_lines.append("")
        for f in result.failed:
            md_lines.append(f"- {f['paper_id']}: {f['error']}")
        md_lines.append("")
    (output_dir / "bench_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    return result


def run_bench_from_spec_path(spec_path: Path, output_dir: Path) -> BenchResult:
    spec = load_bench_spec(spec_path)
    return run_bench(spec, output_dir)
