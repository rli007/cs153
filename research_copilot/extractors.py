from __future__ import annotations

import re
from pathlib import Path


CLAIM_HINTS = (
    "achieve",
    "outperform",
    "improve",
    "reduce",
    "increase",
    "state-of-the-art",
    "sota",
    "accuracy",
    "f1",
    "auc",
    "bleu",
    "rouge",
    "perplexity",
)

DETAIL_HINTS = {
    "random seed": ("seed", "random seed"),
    "hardware": ("gpu", "hardware", "accelerator", "cuda"),
    "data split": ("split", "validation", "test set"),
    "hyperparameters": ("learning rate", "batch size", "epochs", "optimizer"),
    "checkpoint": ("checkpoint", "weights", "model version"),
    "evaluation script": ("eval", "evaluation script", "metric implementation"),
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_claims(paper_text: str, limit: int = 6) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paper_text.strip())
    claims: list[str] = []
    for sentence in sentences:
        normalized = sentence.lower()
        if any(hint in normalized for hint in CLAIM_HINTS):
            claims.append(" ".join(sentence.split()))
        if len(claims) >= limit:
            break
    return claims or ["No explicit metric claim detected yet; add LLM-based claim extraction next."]


def identify_missing_details(paper_text: str, model_card_text: str = "") -> list[str]:
    combined = f"{paper_text}\n{model_card_text}".lower()
    missing: list[str] = []
    for label, hints in DETAIL_HINTS.items():
        if not any(hint in combined for hint in hints):
            missing.append(label)
    return missing
