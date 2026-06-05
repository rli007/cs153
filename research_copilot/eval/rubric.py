"""Rubric and scoring for an audit against hand-curated ground truth.

Spec format (JSON):

```json
{
  "name": "case-studies-v1",
  "description": "Free-form text",
  "papers": [
    {
      "id": "sample",
      "paper": "examples/sample_paper.txt",
      "repo": ".",
      "benchmark": "reproduce the macro F1 improvement on the validation split",
      "model_card": "examples/sample_model_card.txt",
      "reviews": null,
      "ground_truth": {
        "expected_claim_keywords": [
          ["macro", "F1", "78.4"],
          ["annotation", "time"]
        ],
        "expected_missing_categories": ["random_seed", "hardware", "checkpoint"],
        "expected_code_links": {
          "macro": ["research_copilot/extract/claims.py"]
        },
        "min_feasibility": "medium"
      }
    }
  ]
}
```

Scoring axes:

- **claim_coverage** (recall): for each ``expected_claim_keywords`` row, the
  audit must contain a claim whose statement (lowercased) contains every
  keyword in that row.
- **gap_detection** (precision/recall): does the audit's
  ``overall_missing`` cover the expected categories?
- **link_accuracy**: for each substring->expected paths mapping, did the
  matching claim's code-link list contain at least one expected path?
- **feasibility_calibration**: did ``overall_feasibility`` meet
  ``min_feasibility``?
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from research_copilot.schemas import AuditReport


Feasibility = Literal["low", "medium", "high"]
_FEAS_RANK = {"low": 0, "medium": 1, "high": 2}


@dataclass
class GroundTruth:
    expected_claim_keywords: list[list[str]] = field(default_factory=list)
    expected_missing_categories: list[str] = field(default_factory=list)
    expected_code_links: dict[str, list[str]] = field(default_factory=dict)
    min_feasibility: Feasibility | None = None


@dataclass
class PaperEntry:
    id: str
    paper: str
    repo: str
    benchmark: str
    model_card: str | None = None
    reviews: str | None = None
    ground_truth: GroundTruth = field(default_factory=GroundTruth)


@dataclass
class BenchSpec:
    name: str
    description: str
    papers: list[PaperEntry]


@dataclass
class RubricScores:
    claim_coverage: float
    gap_precision: float
    gap_recall: float
    gap_f1: float
    link_accuracy: float
    feasibility_pass: bool

    def aggregate(self) -> float:
        bits = [
            self.claim_coverage,
            self.gap_f1,
            self.link_accuracy,
            1.0 if self.feasibility_pass else 0.0,
        ]
        return sum(bits) / len(bits)


@dataclass
class PaperScore:
    paper_id: str
    rubric: RubricScores
    notes: list[str] = field(default_factory=list)


def load_bench_spec(path: Path) -> BenchSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    papers = []
    for raw in data.get("papers", []):
        gt_raw = raw.get("ground_truth", {}) or {}
        papers.append(
            PaperEntry(
                id=raw["id"],
                paper=raw["paper"],
                repo=raw["repo"],
                benchmark=raw["benchmark"],
                model_card=raw.get("model_card"),
                reviews=raw.get("reviews"),
                ground_truth=GroundTruth(
                    expected_claim_keywords=[
                        list(row) for row in gt_raw.get("expected_claim_keywords", [])
                    ],
                    expected_missing_categories=list(
                        gt_raw.get("expected_missing_categories", [])
                    ),
                    expected_code_links={
                        k: list(v) for k, v in (gt_raw.get("expected_code_links") or {}).items()
                    },
                    min_feasibility=gt_raw.get("min_feasibility"),
                ),
            )
        )
    return BenchSpec(
        name=data.get("name", path.stem),
        description=data.get("description", ""),
        papers=papers,
    )


def _all_keywords_match(haystack: str, keywords: list[str]) -> bool:
    h = haystack.lower()
    return all(kw.lower() in h for kw in keywords)


def _score_claim_coverage(report: AuditReport, gt: GroundTruth) -> tuple[float, list[str]]:
    if not gt.expected_claim_keywords:
        return 1.0, ["claim_coverage: no expected keywords; trivially 1.0"]
    statements = [a.claim.statement for a in report.claims]
    matches = 0
    notes: list[str] = []
    for row in gt.expected_claim_keywords:
        if any(_all_keywords_match(s, row) for s in statements):
            matches += 1
        else:
            notes.append(f"missing claim with keywords {row}")
    return matches / len(gt.expected_claim_keywords), notes


def _score_gap_detection(
    report: AuditReport, gt: GroundTruth
) -> tuple[float, float, float, list[str]]:
    if not gt.expected_missing_categories:
        return 1.0, 1.0, 1.0, []
    found = {m.category for m in report.overall_missing}
    expected = set(gt.expected_missing_categories)
    tp = len(found & expected)
    precision = tp / len(found) if found else 0.0
    recall = tp / len(expected) if expected else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    notes: list[str] = []
    missing_from_audit = expected - found
    if missing_from_audit:
        notes.append(f"gap_detection: did not flag {sorted(missing_from_audit)}")
    extras = found - expected
    if extras:
        notes.append(f"gap_detection: extra (possibly false-positive) flags: {sorted(extras)}")
    return precision, recall, f1, notes


def _score_link_accuracy(report: AuditReport, gt: GroundTruth) -> tuple[float, list[str]]:
    if not gt.expected_code_links:
        return 1.0, []
    notes: list[str] = []
    correct = 0
    total = 0
    for substring, expected_paths in gt.expected_code_links.items():
        total += 1
        matched_audit = next(
            (a for a in report.claims if substring.lower() in a.claim.statement.lower()),
            None,
        )
        if matched_audit is None:
            notes.append(f"link_accuracy: no audited claim contained substring {substring!r}")
            continue
        link_paths = {link.path for link in matched_audit.code_links}
        if any(p in link_paths for p in expected_paths):
            correct += 1
        else:
            notes.append(
                f"link_accuracy: claim {substring!r} links={sorted(link_paths)}, expected one of {expected_paths}"
            )
    return (correct / total) if total else 1.0, notes


def _score_feasibility(report: AuditReport, gt: GroundTruth) -> tuple[bool, list[str]]:
    if not gt.min_feasibility:
        return True, []
    actual_rank = _FEAS_RANK.get(report.overall_feasibility, 0)
    needed_rank = _FEAS_RANK.get(gt.min_feasibility, 0)
    passed = actual_rank >= needed_rank
    notes = (
        []
        if passed
        else [f"feasibility: got {report.overall_feasibility}, expected >= {gt.min_feasibility}"]
    )
    return passed, notes


def score_audit(report: AuditReport, gt: GroundTruth) -> PaperScore:
    coverage, n1 = _score_claim_coverage(report, gt)
    precision, recall, f1, n2 = _score_gap_detection(report, gt)
    link_accuracy, n3 = _score_link_accuracy(report, gt)
    feasibility_pass, n4 = _score_feasibility(report, gt)

    return PaperScore(
        paper_id=report.paper_id or "(unknown)",
        rubric=RubricScores(
            claim_coverage=coverage,
            gap_precision=precision,
            gap_recall=recall,
            gap_f1=f1,
            link_accuracy=link_accuracy,
            feasibility_pass=feasibility_pass,
        ),
        notes=n1 + n2 + n3 + n4,
    )
