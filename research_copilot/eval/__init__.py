"""Evaluation harness for the reproducibility audit pipeline."""

from research_copilot.eval.bench import BenchResult, run_bench
from research_copilot.eval.rubric import (
    BenchSpec,
    GroundTruth,
    PaperScore,
    RubricScores,
    load_bench_spec,
    score_audit,
)

__all__ = [
    "BenchResult",
    "BenchSpec",
    "GroundTruth",
    "PaperScore",
    "RubricScores",
    "load_bench_spec",
    "run_bench",
    "score_audit",
]
