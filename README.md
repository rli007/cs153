# Research Workflow Copilot

A reproducibility audit copilot. Given a research paper (text, PDF, or arXiv
id) and an implementation repo (local path or GitHub URL), it produces an
evidence-grounded **reproduction audit**: structured empirical claims, missing
implementation details, candidate code links retrieved from the repo, per-claim
feasibility scores, blockers, and concrete next steps.

The system never executes user code. It is designed to sit *in front of* a
heavier reproduction agent (or a human re-implementer) and tell them whether a
paper is even worth attempting, what's missing, and which files to start from.

## How it differs from existing work

Most autonomous "paper reproduction" agents (AutoReproduce, DeepRepro,
ReproAgent, ReproLab, AI Scientist) try to *re-implement and run* the paper
end to end. They are heavy, slow, and expensive. This project instead focuses
on the **audit**: structured claim extraction, paper-level gap detection,
claim-to-code traceability via local embedding retrieval, and a measurable
rubric — all in a small number of LLM calls and zero code execution. That's
a useful primitive on its own and a clean front end for a heavier execution
stage later.

## Architecture

```
research_copilot/
  cli.py            argparse with audit | bench subcommands
  workflow.py       4-step orchestration
  llm.py            OpenRouter client: rotation, rate-limit, cache, JSON repair
  config.py         model routes, paths, .env loading
  schemas.py        Pydantic models for the audit
  audit.py          per-claim code links, blockers, feasibility (uses retrieval)
  ingest/
    paper.py        text / PDF / arXiv ingest
    repo.py         local path / GitHub URL, filesystem walk
    huggingface.py  raw model-card fetch from HuggingFace URLs
    openreview.py   public review thread fetch from OpenReview URLs
  retrieve/
    chunker.py      walk + chunk text/code files (~80 lines, 16-line overlap)
    embedder.py     sentence-transformers MiniLM with disk-cached vectors
    code_search.py  cosine-sim CodeIndex + claim->query helpers
  extract/
    claims.py       LLM: structured empirical claims w/ evidence quotes
    missing.py      LLM: missing reproducibility details + severity
    repo.py         LLM: tag entry points / eval scripts / configs
  eval/
    rubric.py       hand-curated ground-truth scoring
    bench.py        run a JSON spec, emit per-paper audits + aggregate
  writers.py        Markdown + JSON serialization
benchmarks/
  case_studies.json sample bench spec
  README.md
```

Total per audit: 4 cold LLM calls (extract claims, detect missing, enrich
repo, audit claims). Embeddings run locally (`all-MiniLM-L6-v2`, ~80MB).
Cache hits cost zero.

## Setup

Requires Python >= 3.10 and an OpenRouter account.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
cp .env.example .env
# edit .env, add OPENROUTER_API_KEY
```

The free tier on OpenRouter gives 20 requests/minute, 50 requests/day with no
credits, or 1000 requests/day after depositing $10. The pipeline rotates
across multiple `:free` model IDs to spread load. Edit `MODEL_ROUTES` in
`research_copilot/config.py` if a particular free model is unavailable.

## Quick start

### Single audit

Local file + local repo:

```bash
python -m research_copilot audit \
  --paper examples/sample_paper.txt \
  --repo . \
  --benchmark "reproduce the macro F1 improvement on the held-out validation split" \
  --model-card examples/sample_model_card.txt \
  --output outputs/audit.md
```

arXiv + GitHub + HuggingFace + OpenReview:

```bash
python -m research_copilot audit \
  --paper 2501.12345 \
  --repo https://github.com/some-user/some-repo \
  --model-card https://huggingface.co/some-user/some-model \
  --reviews https://openreview.net/forum?id=ABC123 \
  --benchmark "reproduce the headline accuracy on ImageNet-1k" \
  --output outputs/audit.json
```

Add `--no-retrieval` to skip local embeddings (faster, less accurate).

### Bench (eval harness)

```bash
python -m research_copilot bench \
  --spec benchmarks/case_studies.json \
  --out outputs/bench/case_studies
```

Writes one folder per paper containing `audit.md` + `audit.json`, plus
aggregate `bench_summary.md` and `bench_summary.json` at the root.

## Rubric

Each paper in a bench spec has hand-curated ground truth. The rubric scores:

- `claim_coverage` — recall over expected claim-keyword rows.
- `gap_f1` — precision/recall over `expected_missing_categories`.
- `link_accuracy` — for each `claim_substring -> [expected_paths]`, did the
  matching audited claim's `code_links` include at least one expected path?
- `feasibility_pass` — did `overall_feasibility` meet `min_feasibility`?

See `benchmarks/README.md` for the spec schema.

## Roadmap

Planned next:

- Add 5–10 real papers to `benchmarks/case_studies.json` with hand-graded
  ground truth, and run a comparison of `--retrieval` vs `--no-retrieval`.
- PaperBench-style rubric adapter (predict atomic rubric satisfaction without
  running the experiment).
- Optional execution mode: opt-in smoke tests in a venv sandbox.
- A `--judge-model` flag to use a paid reasoning model on the audit step
  while keeping extraction on the free tier.
