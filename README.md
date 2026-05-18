# Research Workflow Copilot

An applied-AI scaffold for converting research artifacts into reproducible experiment workflows.

The long-term goal is not to build another paper summarizer. The system is framed as an AI research copilot that takes a paper, repository, benchmark/task description, and optional model card, then produces an executable reproduction plan with scripts, configs, evaluation notes, and a summary of what reproduced.

## Current Scaffold

This repository currently includes a small standard-library Python CLI that:

- accepts a paper text file, repository path, benchmark/task description, and optional model card
- extracts candidate empirical claims from the paper text
- identifies likely missing implementation details
- proposes a staged experiment plan
- writes the result as Markdown or JSON

## Quick Start

```bash
python -m research_copilot --paper examples/sample_paper.txt --repo . --benchmark "reproduce the main accuracy claim on a small validation split" --model-card examples/sample_model_card.txt --output outputs/plan.md
```

## Project Direction

Future versions should add robust PDF parsing, retrieval over technical docs, deeper code understanding, LLM-based claim extraction, experiment orchestration, and evaluation reporting.
