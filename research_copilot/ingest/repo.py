"""Repo ingest: scan a local repo (or shallow-clone a GitHub URL) and summarize."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from research_copilot.config import PROJECT_ROOT, ensure_dirs


_GITHUB_URL = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/([^/\s]+)/([^/\s]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)

_REPO_CACHE = PROJECT_ROOT / ".cache" / "repos"

_IMPORTANT_FILES = (
    "README.md",
    "README.rst",
    "README",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "environment.yml",
    "environment.yaml",
    "Dockerfile",
    "Makefile",
    "configs",
    "config.yaml",
    "config.yml",
    "train.py",
    "main.py",
    "run.py",
    "evaluate.py",
    "eval.py",
)

_SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"}
_TEXT_EXTS = {
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
}


@dataclass(frozen=True)
class FileSummary:
    path: str
    head: str  # first ~40 lines
    size_bytes: int


@dataclass(frozen=True)
class RepoFiles:
    root: Path
    source: str
    important_files: list[str]
    python_scripts: list[str]
    config_files: list[str]
    dependency_files: list[str]
    has_tests: bool
    file_summaries: list[FileSummary] = field(default_factory=list)
    tree_listing: str = ""


def _looks_like_github(value: str) -> bool:
    return bool(_GITHUB_URL.match(value.strip()))


def _shallow_clone(url: str) -> Path:
    ensure_dirs()
    _REPO_CACHE.mkdir(parents=True, exist_ok=True)
    match = _GITHUB_URL.match(url.strip())
    if not match:
        raise ValueError(f"Not a GitHub URL: {url!r}")
    owner, repo = match.group(1), match.group(2)
    target = _REPO_CACHE / f"{owner}__{repo}"
    if target.exists():
        return target
    subprocess.run(
        ["git", "clone", "--depth", "1", f"https://github.com/{owner}/{repo}.git", str(target)],
        check=True,
        capture_output=True,
    )
    return target


def _walk(root: Path, max_files: int = 400) -> list[Path]:
    out: list[Path] = []
    for path in root.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            out.append(path)
            if len(out) >= max_files:
                break
    return out


def _head_of(path: Path, max_lines: int = 40, max_chars: int = 2000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    lines = text.splitlines()[:max_lines]
    head = "\n".join(lines)
    return head[:max_chars]


def _build_tree(root: Path, files: list[Path], max_entries: int = 200) -> str:
    rels = sorted(str(p.relative_to(root)) for p in files)[:max_entries]
    return "\n".join(rels)


def load_repo(value: str | Path) -> RepoFiles:
    """Load a repo from a local path or a GitHub URL (shallow-cloned)."""

    if isinstance(value, str) and _looks_like_github(value):
        root = _shallow_clone(value)
        source = value
    else:
        root = Path(value).resolve()
        source = str(root)

    if not root.exists():
        raise FileNotFoundError(f"Repo path does not exist: {root}")

    files = _walk(root)
    rel_paths = [str(p.relative_to(root)) for p in files]

    important = [name for name in _IMPORTANT_FILES if any(rp == name or rp.startswith(name + "/") for rp in rel_paths)]
    python_scripts = sorted(rp for rp in rel_paths if rp.endswith(".py"))[:60]
    config_files = sorted(
        rp for rp in rel_paths if rp.endswith((".yaml", ".yml", ".toml", ".cfg", ".ini", ".json"))
    )[:40]
    dependency_files = sorted(
        rp
        for rp in rel_paths
        if Path(rp).name
        in {"requirements.txt", "pyproject.toml", "setup.py", "environment.yml", "environment.yaml", "poetry.lock", "uv.lock"}
    )
    has_tests = any(
        any(part in {"tests", "test"} for part in Path(rp).parts) or Path(rp).name.startswith("test_")
        for rp in rel_paths
    )

    summary_paths = [p for p in files if p.suffix in _TEXT_EXTS][:30]
    file_summaries = [
        FileSummary(
            path=str(p.relative_to(root)),
            head=_head_of(p),
            size_bytes=p.stat().st_size,
        )
        for p in summary_paths
    ]

    return RepoFiles(
        root=root,
        source=source,
        important_files=important,
        python_scripts=python_scripts,
        config_files=config_files,
        dependency_files=dependency_files,
        has_tests=has_tests,
        file_summaries=file_summaries,
        tree_listing=_build_tree(root, files),
    )
