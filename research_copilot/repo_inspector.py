from __future__ import annotations

from pathlib import Path


IMPORTANT_FILES = (
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "environment.yml",
    "Dockerfile",
)


def inspect_repo(repo_path: Path) -> dict[str, object]:
    files = {path.name for path in repo_path.iterdir()} if repo_path.exists() else set()
    scripts = sorted(
        str(path.relative_to(repo_path))
        for path in repo_path.rglob("*.py")
        if ".git" not in path.parts
    )[:20]

    return {
        "path": str(repo_path),
        "exists": repo_path.exists(),
        "important_files": [name for name in IMPORTANT_FILES if name in files],
        "python_scripts": scripts,
        "has_tests": any(part in {"tests", "test"} for path in repo_path.rglob("*") for part in path.parts),
    }
