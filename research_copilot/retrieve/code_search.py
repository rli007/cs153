"""Cosine-similarity index over repo chunks plus claim->query helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from research_copilot.ingest import RepoFiles
from research_copilot.retrieve.chunker import CodeChunk, chunk_repo
from research_copilot.retrieve.embedder import embed_texts
from research_copilot.schemas import Claim


@dataclass
class CodeIndex:
    chunks: list[CodeChunk]
    embeddings: np.ndarray  # (n, d), L2-normalized

    def search(self, query: str, *, k: int = 8) -> list[tuple[CodeChunk, float]]:
        if not self.chunks:
            return []
        q_vec = embed_texts([query])
        if q_vec.size == 0:
            return []
        scores = (self.embeddings @ q_vec[0]).astype(float)
        order = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in order]

    @property
    def is_empty(self) -> bool:
        return len(self.chunks) == 0


def build_index(repo: RepoFiles, *, chunk_lines: int = 80) -> CodeIndex:
    chunks = chunk_repo(repo, chunk_lines=chunk_lines)
    if not chunks:
        return CodeIndex(chunks=[], embeddings=np.zeros((0, 384), dtype=np.float32))
    texts = [_chunk_for_embedding(c) for c in chunks]
    embeddings = embed_texts(texts)
    return CodeIndex(chunks=chunks, embeddings=embeddings)


def _chunk_for_embedding(chunk: CodeChunk) -> str:
    """Compact representation that includes the path for retrieval signal."""
    return f"{chunk.path}\n{chunk.text}"


def query_for_claim(claim: Claim) -> str:
    parts: list[str] = [claim.statement]
    if claim.method_name:
        parts.append(f"method: {claim.method_name}")
    if claim.baseline_name:
        parts.append(f"baseline: {claim.baseline_name}")
    if claim.metric:
        parts.append(f"metric: {claim.metric.name}")
    if claim.dataset:
        parts.append(f"dataset: {claim.dataset.name}")
        if claim.dataset.split:
            parts.append(f"split: {claim.dataset.split}")
    return " | ".join(parts)


def search_for_claim(
    index: CodeIndex, claim: Claim, *, k: int = 8
) -> list[tuple[CodeChunk, float]]:
    if index.is_empty:
        return []
    return index.search(query_for_claim(claim), k=k)
