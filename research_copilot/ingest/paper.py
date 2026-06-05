"""Paper ingest: plain text, local PDF, or arXiv id/url.

The same ``load_paper`` entry point handles all three. arXiv inputs are cached
on disk so re-runs do not re-download.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from research_copilot.config import PAPER_CACHE_DIR, ensure_dirs


@dataclass(frozen=True)
class PaperText:
    raw_text: str
    pages: list[str]
    source: str
    char_count: int
    metadata: dict = field(default_factory=dict)


_ARXIV_ID = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?",
    re.IGNORECASE,
)


def _looks_like_arxiv(value: str) -> bool:
    if value.lower().startswith(("http://", "https://")):
        return "arxiv.org" in value.lower()
    return bool(_ARXIV_ID.fullmatch(value.strip()))


def _parse_arxiv_id(value: str) -> str:
    match = _ARXIV_ID.search(value)
    if not match:
        raise ValueError(f"Could not parse an arXiv id from {value!r}.")
    return match.group(1)


def _read_pdf(path: Path) -> tuple[str, list[str]]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError(
            "pdfplumber is required for PDF ingest. Install with `pip install pdfplumber`."
        ) from exc

    pages: list[str] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n\n".join(pages), pages


def _fetch_arxiv(value: str) -> tuple[Path, dict]:
    """Fetch an arXiv paper via direct HTTPS (faster + no extra deps than the ``arxiv`` lib)."""

    import httpx

    ensure_dirs()
    arxiv_id = _parse_arxiv_id(value)
    pdf_path = PAPER_CACHE_DIR / f"{arxiv_id}.pdf"
    meta_path = PAPER_CACHE_DIR / f"{arxiv_id}.meta.json"

    metadata = {"arxiv_id": arxiv_id, "pdf_path": str(pdf_path)}
    if meta_path.exists():
        try:
            import json as _json

            metadata.update(_json.loads(meta_path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            pass

    if not pdf_path.exists():
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            pdf_path.write_bytes(r.content)

            try:
                import re as _re

                meta_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
                rm = client.get(meta_url, timeout=20.0)
                if rm.status_code == 200:
                    text = rm.text
                    title_m = _re.search(
                        r"<entry>.*?<title>(.*?)</title>",
                        text,
                        flags=_re.DOTALL,
                    )
                    authors = _re.findall(r"<author>\s*<name>(.*?)</name>", text)
                    summary_m = _re.search(
                        r"<entry>.*?<summary>(.*?)</summary>",
                        text,
                        flags=_re.DOTALL,
                    )
                    if title_m:
                        metadata["title"] = " ".join(title_m.group(1).split())
                    if authors:
                        metadata["authors"] = authors
                    if summary_m:
                        metadata["summary"] = " ".join(summary_m.group(1).split())
                    import json as _json

                    meta_path.write_text(_json.dumps(metadata, indent=2), encoding="utf-8")
            except httpx.HTTPError:
                pass

    return pdf_path, metadata


def load_paper(value: str | Path) -> PaperText:
    """Load a paper from a text file, PDF, or arXiv id/url."""

    if isinstance(value, Path) or "/" in str(value) or "\\" in str(value) or "." in str(value).split("/")[-1]:
        path = Path(value)
        if path.exists():
            if path.suffix.lower() == ".pdf":
                raw, pages = _read_pdf(path)
                return PaperText(
                    raw_text=raw,
                    pages=pages,
                    source=str(path),
                    char_count=len(raw),
                    metadata={"kind": "pdf", "path": str(path)},
                )
            raw = path.read_text(encoding="utf-8")
            return PaperText(
                raw_text=raw,
                pages=[raw],
                source=str(path),
                char_count=len(raw),
                metadata={"kind": "text", "path": str(path)},
            )

    if _looks_like_arxiv(str(value)):
        pdf_path, meta = _fetch_arxiv(str(value))
        raw, pages = _read_pdf(pdf_path)
        meta["kind"] = "arxiv"
        return PaperText(
            raw_text=raw,
            pages=pages,
            source=f"arxiv:{meta['arxiv_id']}",
            char_count=len(raw),
            metadata=meta,
        )

    raise FileNotFoundError(
        f"Could not interpret {value!r} as a text file, PDF, or arXiv reference."
    )
