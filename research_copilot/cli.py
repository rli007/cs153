"""Command-line entry point for the reproducibility audit copilot.

Two subcommands:

- ``audit`` — run a single audit (paper + repo) and write Markdown/JSON.
- ``bench`` — run a JSON bench spec, score every audit against ground truth,
  and emit per-paper audits plus aggregate metrics.

For backward compatibility, calling the program with no subcommand but with
the ``--paper / --repo / --benchmark`` flags is treated as ``audit``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from research_copilot.eval import run_bench
from research_copilot.eval.rubric import load_bench_spec
from research_copilot.workflow import CopilotInput, build_audit
from research_copilot.writers import write_json, write_markdown


def _add_audit_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--paper",
        required=True,
        help="Path to a .txt or .pdf, or an arXiv id/url (e.g. 2501.12345).",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Path to a local repository, or a GitHub URL (will be shallow-cloned).",
    )
    parser.add_argument(
        "--benchmark",
        required=True,
        help="Benchmark or task you want to reproduce, in plain English.",
    )
    parser.add_argument(
        "--model-card",
        default=None,
        help="Optional file path or HuggingFace URL (huggingface.co/<org>/<model>).",
    )
    parser.add_argument(
        "--reviews",
        default=None,
        help="Optional OpenReview forum URL or note id; reviewer concerns help find missing details.",
    )
    parser.add_argument(
        "--output",
        default="outputs/audit.md",
        help="Output path. Use a .md or .json extension to pick the format.",
    )
    parser.add_argument(
        "--no-retrieval",
        action="store_true",
        help="Disable local embedding-based retrieval over the repo (faster, fewer signals).",
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="research-copilot",
        description=(
            "Reproducibility audit copilot. ``audit`` runs a single paper-and-repo audit; "
            "``bench`` scores audits against a hand-curated rubric."
        ),
    )
    sub = parser.add_subparsers(dest="command")

    audit_parser = sub.add_parser("audit", help="Run a single audit.")
    _add_audit_args(audit_parser)

    bench_parser = sub.add_parser("bench", help="Run a bench spec and score audits.")
    bench_parser.add_argument("--spec", required=True, help="Path to a bench spec JSON.")
    bench_parser.add_argument(
        "--out",
        default="outputs/bench",
        help="Output directory; one subfolder per paper plus bench_summary.{md,json}.",
    )

    # Backward compatibility: accept top-level audit flags too.
    _add_audit_args(parser)
    return parser


def _run_audit(args: argparse.Namespace) -> int:
    inputs = CopilotInput(
        paper=args.paper,
        repo=args.repo,
        benchmark=args.benchmark,
        model_card=args.model_card,
        reviews=args.reviews,
        use_retrieval=not args.no_retrieval,
    )
    try:
        report = build_audit(inputs)
    except Exception as exc:
        print(f"audit failed: {exc}", file=sys.stderr)
        return 1
    output_path = Path(args.output)
    if output_path.suffix.lower() == ".json":
        write_json(report, output_path)
    else:
        write_markdown(report, output_path)
    print(f"Wrote reproduction audit to {output_path}")
    return 0


def _run_bench(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"bench spec not found: {spec_path}", file=sys.stderr)
        return 1
    spec = load_bench_spec(spec_path)
    out_dir = Path(args.out)
    result = run_bench(spec, out_dir)
    print(
        f"Bench '{spec.name}' \u2014 papers={len(result.paper_scores)} "
        f"failed={len(result.failed)} aggregate={result.aggregate_score:.3f}"
    )
    print(
        f"  claim_coverage={result.aggregate_claim_coverage:.3f} "
        f"gap_f1={result.aggregate_gap_f1:.3f} "
        f"link_accuracy={result.aggregate_link_accuracy:.3f} "
        f"feasibility_pass_rate={result.feasibility_pass_rate:.3f}"
    )
    print(f"  wrote: {out_dir}/bench_summary.md")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = _build_parser()
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "bench":
        return _run_bench(args)
    if args.command == "audit" or args.command is None:
        if not getattr(args, "paper", None):
            parser.print_help()
            return 1
        return _run_audit(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
