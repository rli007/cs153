"""Ingest helpers: convert paper / repo / model-card / reviews sources into our internal types."""

from research_copilot.ingest.huggingface import load_model_card
from research_copilot.ingest.openreview import load_reviews
from research_copilot.ingest.paper import PaperText, load_paper
from research_copilot.ingest.repo import RepoFiles, load_repo

__all__ = [
    "PaperText",
    "load_paper",
    "RepoFiles",
    "load_repo",
    "load_model_card",
    "load_reviews",
]
