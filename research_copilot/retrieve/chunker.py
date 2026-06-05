"""Repository chunker.

Walks the repository's text-like files and splits them into overlapping chunks
suitable for embedding. We keep the chunks small enough (~80 lines) to be
useful as discrete code-link candidates and large enough to carry semantic
context.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_copilot.ingest import RepoFiles


_CHUNKABLE_EXTS = {
    ".py",
    ".md",
    ".rst",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".cfg",
    ".ini",
    ".sh",
    ".json",
    ".js",
    ".ts",
    ".go",
    ".rs",
    ".java",
    ".cpp",
    ".c",
    ".h",
    ".hpp",
}

_KIND_FOR_EXT = {
    ".md": "doc",
    ".rst": "doc",
    ".txt": "doc",
    ".yaml": "config",
    ".yml": "config",
    ".toml": "config",
    ".cfg": "config",
    ".ini": "config",
    ".json": "config",
}


@dataclass(frozen=True)
class CodeChunk:
    path: str
    start_line: int
    end_line: int
    text: str
    kind: str

    def display(self, max_chars: int = 600) -> str:
        snippet = self.text
        if len(snippet) > max_chars:
            snippet = snippet[: max_chars - 3] + "..."
        return f"{self.path}:{self.start_line}-{self.end_line}\n{snippet}"


def _chunk_text(
    path: str,
    text: str,
    *,
    kind: str,
    chunk_lines: int = 80,
    overlap_lines: int = 16,
) -> list[CodeChunk]:
    if not text.strip():
        return []
    lines = text.splitlines()
    if len(lines) <= chunk_lines:
        return [
            CodeChunk(
                path=path,
                start_line=1,
                end_line=len(lines),
                text=text,
                kind=kind,
            )
        ]

    step = max(1, chunk_lines - overlap_lines)
    chunks: list[CodeChunk] = []
    for start in range(0, len(lines), step):
        end = min(len(lines), start + chunk_lines)
        chunk_text = "\n".join(lines[start:end])
        if not chunk_text.strip():
            continue
        chunks.append(
            CodeChunk(
                path=path,
                start_line=start + 1,
                end_line=end,
                text=chunk_text,
                kind=kind,
            )
        )
        if end == len(lines):
            break
    return chunks


def _read_safely(path: Path, max_bytes: int = 200_000) -> str | None:
    try:
        if path.stat().st_size > max_bytes:
            return None
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def chunk_repo(
    repo: RepoFiles,
    *,
    chunk_lines: int = 80,
    overlap_lines: int = 16,
    max_files: int = 250,
    max_chunks: int = 1500,
) -> list[CodeChunk]:
    """Walk the repo and produce a flat list of chunks ready to embed."""

    skip_parts = {
        ".git",
        "__pycache__",
        "node_modules",
        ".venv",
        "venv",
        "dist",
        "build",
        ".cache",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
    }
    chunks: list[CodeChunk] = []
    seen = 0
    for path in repo.root.rglob("*"):
        if seen >= max_files or len(chunks) >= max_chunks:
            break
        if not path.is_file():
            continue
        try:
            rel_path = path.relative_to(repo.root)
        except ValueError:
            continue
        if any(part in skip_parts for part in rel_path.parts):
            continue
        suffix = path.suffix.lower()
        if suffix not in _CHUNKABLE_EXTS:
            continue
        text = _read_safely(path)
        if text is None:
            continue
        rel = str(rel_path)
        kind = _KIND_FOR_EXT.get(suffix, "code")
        chunks.extend(
            _chunk_text(rel, text, kind=kind, chunk_lines=chunk_lines, overlap_lines=overlap_lines)
        )
        seen += 1
    return chunks[:max_chunks]
