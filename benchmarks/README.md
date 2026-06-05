# Bench specs

Each `.json` file here describes a set of (paper, repo, benchmark) triples
plus hand-curated ground truth. The runner produces an audit per paper and
scores it against the ground truth using the rubric in
`research_copilot/eval/rubric.py`.

Run a bench:

```bash
python -m research_copilot bench --spec benchmarks/case_studies.json --out outputs/bench/case_studies
```

The runner writes one folder per paper containing `audit.md` and `audit.json`,
plus aggregate `bench_summary.json` / `bench_summary.md` at the root.

## Spec schema

```json
{
  "name": "string",
  "description": "string",
  "papers": [
    {
      "id": "unique-string",
      "paper": "txt|pdf path or arXiv id/url",
      "repo": "local path or GitHub url",
      "benchmark": "natural language description of what to reproduce",
      "model_card": "optional file path or HuggingFace url",
      "reviews": "optional OpenReview url",
      "ground_truth": {
        "expected_claim_keywords": [["k1","k2"], ...],
        "expected_missing_categories": ["random_seed", "hardware", ...],
        "expected_code_links": {
          "claim_substring": ["expected_repo_path", ...]
        },
        "min_feasibility": "low|medium|high"
      }
    }
  ]
}
```

## Rubric

- **claim_coverage**: did the audit produce a claim matching every expected keyword row?
- **gap_f1**: precision/recall over `expected_missing_categories`.
- **link_accuracy**: for each `claim_substring -> expected_paths`, did the matching audited claim's code_links include at least one expected path?
- **feasibility_pass**: did `overall_feasibility` meet or exceed `min_feasibility`?
