"""Local embedding-based retrieval over a repository's text/code files.

Designed to keep zero external API cost: embeddings are computed locally with
``sentence-transformers`` and cached on disk by chunk-text hash so repeat runs
are nearly free.
"""

from research_copilot.retrieve.chunker import CodeChunk, chunk_repo
from research_copilot.retrieve.code_search import (
    CodeIndex,
    build_index,
    query_for_claim,
    search_for_claim,
)
from research_copilot.retrieve.embedder import embed_texts

__all__ = [
    "CodeChunk",
    "CodeIndex",
    "build_index",
    "chunk_repo",
    "embed_texts",
    "query_for_claim",
    "search_for_claim",
]
