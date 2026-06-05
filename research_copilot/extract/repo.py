"""LLM-assisted enrichment of repo signals.

The filesystem walk in :mod:`research_copilot.ingest.repo` finds candidate
files. This module asks a code-tuned model to label which of those files are
the likely training entry points, evaluation scripts, and config files.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from research_copilot.ingest import RepoFiles
from research_copilot.llm import complete_json
from research_copilot.schemas import RepoSignals


_SYSTEM = """\
You are a code reviewer. You are given a listing of files in a repository plus
short head excerpts of the most likely-relevant files. Identify, using ONLY
filenames present in the listing:

- ``likely_entry_points``: scripts that look like ``train``, ``main``, ``run``,
  or anything that a human would invoke to start the headline experiment.
- ``likely_eval_scripts``: scripts that look like evaluation/scoring/inference
  drivers that compute the reported metric.
- ``likely_config_files``: yaml/toml/json/cfg files that hold hyperparameters
  or experiment definitions.
- ``notes``: short bullet observations a researcher should know (e.g., "uses
  Hydra configs under configs/", "no requirements file detected").

Return strict JSON. Do NOT invent filenames that are not in the listing.
"""

_SCHEMA_HINT = (
    'A JSON object with shape: {'
    '"likely_entry_points": [str], '
    '"likely_eval_scripts": [str], '
    '"likely_config_files": [str], '
    '"notes": [str]'
    '}'
)


_MAX_HEAD_CHARS = 1500


def enrich_repo_signals(repo: RepoFiles) -> RepoSignals:
    listing = repo.tree_listing[:8000]
    summaries: list[str] = []
    for fs in repo.file_summaries:
        head = fs.head[:_MAX_HEAD_CHARS]
        summaries.append(f"### {fs.path}\n{head}")
    summaries_block = "\n\n".join(summaries)[:30_000]

    user = (
        "Repository listing (truncated):\n"
        f"{listing}\n\n"
        "File excerpts (truncated):\n"
        f"{summaries_block}\n\n"
        "Identify entry points, eval scripts, and config files."
    )

    raw, _resp = complete_json(
        role="code",
        system=_SYSTEM,
        user=user,
        schema_hint=_SCHEMA_HINT,
        max_tokens=1500,
    )

    if not isinstance(raw, dict):
        raw = {}

    listing_set = set(repo.tree_listing.splitlines()) | set(repo.python_scripts) | set(repo.config_files)

    def _filter(values: object) -> list[str]:
        if not isinstance(values, list):
            return []
        return [v for v in values if isinstance(v, str) and v in listing_set]

    return RepoSignals(
        path=str(repo.root),
        exists=True,
        important_files=list(repo.important_files),
        likely_entry_points=_filter(raw.get("likely_entry_points")),
        likely_eval_scripts=_filter(raw.get("likely_eval_scripts")),
        likely_config_files=_filter(raw.get("likely_config_files")),
        dependency_files=list(repo.dependency_files),
        has_tests=repo.has_tests,
        notes=[n for n in raw.get("notes", []) if isinstance(n, str)][:10],
    )
