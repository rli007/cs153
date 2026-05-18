# Research Artifact to Reproducible Workflow Plan

## Benchmark

reproduce the main macro F1 improvement on a small validation split

## Candidate Claims

- On the held-out validation split, the method improves macro F1 from 71.2 to 78.4 compared with a sparse baseline.
- The model also reduces average annotation time in a small user study.

## Missing Implementation Details

- random seed

## Repository Summary

- Path: .
- Exists: True
- Important files: README.md, pyproject.toml
- Python scripts: research_copilot/__init__.py, research_copilot/__main__.py, research_copilot/cli.py, research_copilot/extractors.py, research_copilot/repo_inspector.py, research_copilot/workflow.py, research_copilot/writers.py
- Has tests: False

## Experiment Steps

1. Confirm the target claim and metric definition.
2. Map repository entry points to training, inference, and evaluation commands.
3. Create a minimal environment file and smoke-test command.
4. Run a small-scale reproduction pass before attempting the full benchmark.
5. Compare observed metrics against the paper claim and record gaps.

## Risks

- Paper text parsing is currently plain-text only.
- Claim extraction uses heuristics and should be replaced with structured LLM extraction.
- Experiment execution is planned but not yet automated.
