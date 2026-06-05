"""Local sentence-transformer embedder with disk-level caching.

Each unique chunk text is embedded once and cached as a .npy file keyed by
``sha256(model_name + "::" + text)``. This makes incremental runs essentially
free even for large repositories.
"""

from __future__ import annotations

import hashlib
import os

import numpy as np

from research_copilot.config import PROJECT_ROOT


_DEFAULT_MODEL = os.environ.get("RC_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
_CACHE_DIR = PROJECT_ROOT / ".cache" / "embeddings"

_MODEL = None  # lazy-loaded sentence-transformers model


def _model_singleton(model_name: str):
    global _MODEL
    if _MODEL is not None and getattr(_MODEL, "_rc_name", None) == model_name:
        return _MODEL
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(model_name)
    model._rc_name = model_name  # type: ignore[attr-defined]
    _MODEL = model
    return model


def _key(model_name: str, text: str) -> str:
    h = hashlib.sha256()
    h.update(model_name.encode("utf-8"))
    h.update(b"::")
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def embed_texts(
    texts: list[str],
    *,
    model_name: str = _DEFAULT_MODEL,
    batch_size: int = 32,
    use_cache: bool = True,
) -> np.ndarray:
    """Return a (len(texts), dim) float32 matrix of L2-normalized embeddings."""

    if not texts:
        return np.zeros((0, 384), dtype=np.float32)

    _CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cached: dict[int, np.ndarray] = {}
    misses_idx: list[int] = []
    misses_keys: list[str] = []

    for i, text in enumerate(texts):
        key = _key(model_name, text)
        path = _CACHE_DIR / f"{key}.npy"
        if use_cache and path.exists():
            try:
                cached[i] = np.load(path)
                continue
            except (OSError, ValueError):
                pass
        misses_idx.append(i)
        misses_keys.append(key)

    if misses_idx:
        model = _model_singleton(model_name)
        miss_texts = [texts[i] for i in misses_idx]
        encoded = model.encode(
            miss_texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        ).astype(np.float32)
        for slot, key, vec in zip(misses_idx, misses_keys, encoded):
            cached[slot] = vec
            if use_cache:
                np.save(_CACHE_DIR / f"{key}.npy", vec)

    dim = next(iter(cached.values())).shape[0]
    out = np.empty((len(texts), dim), dtype=np.float32)
    for i in range(len(texts)):
        out[i] = cached[i]
    return out
