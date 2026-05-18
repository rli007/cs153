from __future__ import annotations

import argparse
from pathlib import Path

from research_copilot.workflow import CopilotInput, build_reproduction_plan
from research_copilot.writers import write_json, write_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a first-pass reproducibility workflow from research artifacts."
    )
    parser.add_argument("--paper", required=True, help="Path to a text version of the paper.")
    parser.add_argument("--repo", required=True, help="Path to the implementation repository.")
    parser.add_argument("--benchmark", required=True, help="Benchmark or task to reproduce.")
    parser.add_argument("--model-card", help="Optional path to a model card or model notes.")
    parser.add_argument(
        "--output",
        default="outputs/reproduction_plan.md",
        help="Output path ending in .md or .json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paper_path = Path(args.paper)
    repo_path = Path(args.repo)
    model_card_path = Path(args.model_card) if args.model_card else None
    output_path = Path(args.output)

    inputs = CopilotInput(
        paper_path=paper_path,
        repo_path=repo_path,
        benchmark=args.benchmark,
        model_card_path=model_card_path,
    )
    plan = build_reproduction_plan(inputs)

    if output_path.suffix.lower() == ".json":
        write_json(plan, output_path)
    else:
        write_markdown(plan, output_path)

    print(f"Wrote reproduction plan to {output_path}")
