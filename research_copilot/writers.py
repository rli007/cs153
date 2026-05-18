from __future__ import annotations

import json
from pathlib import Path

from research_copilot.workflow import ReproductionPlan


def write_json(plan: ReproductionPlan, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan.to_dict(), indent=2), encoding="utf-8")


def write_markdown(plan: ReproductionPlan, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {plan.title}",
        "",
        f"## Benchmark",
        "",
        plan.benchmark,
        "",
        "## Candidate Claims",
        "",
        *[f"- {claim}" for claim in plan.claims],
        "",
        "## Missing Implementation Details",
        "",
        *[f"- {detail}" for detail in plan.missing_details],
        "",
        "## Repository Summary",
        "",
        f"- Path: {plan.repo_summary['path']}",
        f"- Exists: {plan.repo_summary['exists']}",
        f"- Important files: {', '.join(plan.repo_summary['important_files']) or 'none detected'}",
        f"- Python scripts: {', '.join(plan.repo_summary['python_scripts']) or 'none detected'}",
        f"- Has tests: {plan.repo_summary['has_tests']}",
        "",
        "## Experiment Steps",
        "",
        *[f"{index}. {step}" for index, step in enumerate(plan.experiment_steps, start=1)],
        "",
        "## Risks",
        "",
        *[f"- {risk}" for risk in plan.risks],
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
