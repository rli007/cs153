"""Streamlit demo UI for the Research Workflow Copilot.

Run with: ``streamlit run app.py``

Designed for live video demo: paste an arXiv id and a GitHub URL, click Run,
and watch the audit produce structured claims, missing details, code links,
and a feasibility verdict. Pre-loaded examples surface known-good runs from
the on-disk LLM cache (zero cost, instant playback).
"""

from __future__ import annotations

from html import escape
import json
import re
import time
from pathlib import Path
from urllib.parse import quote

import httpx
import streamlit as st

from research_copilot.config import MODEL_ROUTES, USE_PREMIUM_MODELS
from research_copilot.workflow import CopilotInput, build_audit
from research_copilot.schemas import AuditReport, ClaimAudit, MissingDetail


st.set_page_config(
    page_title="Repro Audit",
    page_icon="RA",
    layout="wide",
)


# ---------- Styling ----------
st.markdown(
    """
    <style>
      :root {
        --ink: #111111;
        --muted: #666A73;
        --line: #D7D8DA;
        --paper: #F8F7F2;
        --panel: #FFFFFF;
        --acid: #B7FF3C;
        --blue: #365DFF;
        --amber: #FFB000;
        --red: #E5484D;
      }
      html, body, [class*="css"] {
        color: var(--ink);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .stApp {
        background:
          linear-gradient(90deg, rgba(17,17,17,.045) 1px, transparent 1px),
          linear-gradient(180deg, rgba(17,17,17,.035) 1px, transparent 1px),
          var(--paper);
        background-size: 34px 34px;
      }
      section[data-testid="stSidebar"] {
        background: #111111;
        color: #F8F7F2;
        border-right: 1px solid #111111;
      }
      section[data-testid="stSidebar"] label,
      section[data-testid="stSidebar"] p,
      section[data-testid="stSidebar"] span,
      section[data-testid="stSidebar"] h1,
      section[data-testid="stSidebar"] h2,
      section[data-testid="stSidebar"] h3 {
        color: #F8F7F2 !important;
      }
      section[data-testid="stSidebar"] input,
      section[data-testid="stSidebar"] textarea {
        background: #1B1B1B !important;
        color: #F8F7F2 !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 6px !important;
      }
      .block-container {
        padding-top: 2rem;
        max-width: 1240px;
      }
      .brand-mark {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0;
        margin-bottom: 12px;
      }
      .brand-mark span:first-child {
        display: inline-grid;
        place-items: center;
        width: 31px;
        height: 31px;
        background: var(--ink);
        color: var(--acid);
        border: 1px solid var(--ink);
        border-radius: 4px;
      }
      .hero {
        border: 1px solid var(--ink);
        background: var(--panel);
        box-shadow: 7px 7px 0 var(--ink);
        border-radius: 8px;
        padding: 28px 30px 24px;
        margin-bottom: 22px;
      }
      .hero h1 {
        font-size: clamp(34px, 5vw, 68px);
        line-height: .96;
        letter-spacing: 0;
        margin: 0 0 14px;
      }
      .hero p {
        color: #3E4249;
        max-width: 760px;
        font-size: 17px;
        line-height: 1.45;
        margin: 0;
      }
      .signal-row {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 18px 0 4px;
      }
      .signal {
        border: 1px solid var(--ink);
        background: #FDFDF8;
        border-radius: 6px;
        padding: 12px;
      }
      .signal b {
        display: block;
        font-size: 20px;
        line-height: 1.1;
      }
      .signal span {
        color: var(--muted);
        font-size: 12px;
        text-transform: uppercase;
        font-weight: 700;
      }
      .feasibility-high,
      .feasibility-medium,
      .feasibility-low {
        padding: 6px 12px;
        border-radius: 999px;
        font-weight: 800;
        display: inline-block;
        border: 1px solid var(--ink);
      }
      .feasibility-high {background: var(--acid); color: var(--ink);}
      .feasibility-medium {background: var(--amber); color: var(--ink);}
      .feasibility-low {background: var(--red); color: #FFFFFF;}
      .severity-high {color: #B42318; font-weight: 800;}
      .severity-medium {color: #9A5B00; font-weight: 800;}
      .severity-low {color: #247A39; font-weight: 800;}
      .small-muted {color: var(--muted); font-size: 0.85em;}
      .link-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 14px 0 4px;
      }
      .action-link {
        display: inline-flex;
        align-items: center;
        min-height: 34px;
        padding: 7px 12px;
        border-radius: 6px;
        border: 1px solid var(--ink);
        background: #FFFFFF;
        color: var(--ink) !important;
        text-decoration: none !important;
        font-weight: 800;
        font-size: 13px;
      }
      .action-link.primary {
        background: var(--acid);
        box-shadow: 3px 3px 0 var(--ink);
      }
      .action-link.dark {
        background: var(--ink);
        color: #FFFFFF !important;
      }
      .code-link {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-left: 4px solid var(--blue);
        padding: 9px 12px;
        border-radius: 6px;
        margin-bottom: 7px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 0.85em;
      }
      .report-head {
        border: 1px solid var(--ink);
        background: #FFFFFF;
        box-shadow: 6px 6px 0 var(--ink);
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 18px;
      }
      .report-head h2 {
        margin: 0;
        letter-spacing: 0;
      }
      .run-panel {
        border: 1px solid var(--ink);
        background: #FFFFFF;
        border-radius: 8px;
        padding: 18px 20px 20px;
        margin: 16px 0 22px;
        box-shadow: 5px 5px 0 rgba(17,17,17,.92);
      }
      .run-panel h2 {
        margin: 0 0 4px;
        letter-spacing: 0;
      }
      .run-panel p {
        color: #4F535B;
        margin: 0 0 12px;
      }
      .copy-block {
        border: 1px solid var(--line);
        background: #FFFFFF;
        border-radius: 8px;
        padding: 14px 16px;
        margin: 10px 0;
      }
      .copy-block h3 {
        margin-top: 0;
        letter-spacing: 0;
      }
      .copy-block p,
      .copy-block li {
        color: #4F535B;
        line-height: 1.5;
      }
      .anchor-card {
        border: 1px solid var(--ink);
        background: #FFFFFF;
        border-radius: 8px;
        padding: 12px 14px;
        margin: 10px 0;
      }
      .anchor-card h4 {
        margin: 0 0 6px;
        letter-spacing: 0;
      }
      .anchor-meta {
        color: var(--muted);
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
      }
      .snippet {
        background: #111111;
        color: #F8F7F2;
        border-radius: 6px;
        padding: 10px 12px;
        white-space: pre-wrap;
        overflow-x: auto;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 12px;
        line-height: 1.45;
      }
      .email-preview {
        background: #111111;
        color: #F8F7F2;
        border-radius: 8px;
        padding: 14px 16px;
        white-space: pre-wrap;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 13px;
      }
      blockquote {
        border-left: 3px solid var(--blue);
        padding-left: 12px;
        color: #3E4249;
      }
      div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 12px;
      }
      div[data-testid="stButton"] button {
        border-radius: 6px;
        border: 1px solid #F8F7F2;
        background: var(--acid);
        color: var(--ink);
        font-weight: 800;
      }
      @media (max-width: 760px) {
        .signal-row {grid-template-columns: repeat(2, minmax(0, 1fr));}
        .hero {padding: 22px 18px;}
      }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Header ----------
st.markdown(
    """
    <div class="brand-mark"><span>RA</span><span>Repro Audit</span></div>
    <div class="hero">
      <h1>Ship a repro decision before the GPU bill lands.</h1>
      <p>
        Evidence-grounded audits for ML papers: claims, missing details,
        repo links, implementation plans, author follow-ups, and a feasibility
        verdict in one review surface.
      </p>
      <div class="signal-row">
        <div class="signal"><b>4</b><span>model calls</span></div>
        <div class="signal"><b>$0.05</b><span>typical run</span></div>
        <div class="signal"><b>6</b><span>paper bench</span></div>
        <div class="signal"><b>0</b><span>code execution</span></div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


examples = {
    "Speculative Decoding (2211.17192)": {
        "paper": "2211.17192",
        "repo": "https://github.com/romsto/Speculative-Decoding",
        "repo_relation": "unofficial public replication",
        "benchmark": "Reproduce the speculative decoding speedup claim: 2x-3x faster inference than standard autoregressive decoding while preserving the target model output distribution.",
        "model_card": None,
    },
    "Chain-of-Thought Prompting (2201.11903)": {
        "paper": "2201.11903",
        "repo": "https://github.com/FranxYao/chain-of-thought-hub",
        "repo_relation": "unofficial public benchmark/reproduction hub",
        "benchmark": "Reproduce the chain-of-thought prompting claim on GSM8K: few-shot CoT prompting substantially improves large-model math reasoning accuracy over standard prompting.",
        "model_card": None,
    },
    "(custom)": None,
    "Sample (toy)": {
        "paper": "examples/sample_paper.txt",
        "repo": ".",
        "repo_relation": "local sample repository",
        "benchmark": "reproduce the macro F1 improvement on the held-out validation split",
        "model_card": "examples/sample_model_card.txt",
    },
    "LoRA (2106.09685)": {
        "paper": "2106.09685",
        "repo": "https://github.com/microsoft/LoRA",
        "repo_relation": "official author/lab implementation",
        "benchmark": "Reproduce LoRA fine-tuning of GPT-2 medium on E2E NLG (Table 2 BLEU/ROUGE).",
        "model_card": None,
    },
    "FlashAttention (2205.14135)": {
        "paper": "2205.14135",
        "repo": "https://github.com/Dao-AILab/flash-attention",
        "repo_relation": "official author/lab implementation",
        "benchmark": "Reproduce FlashAttention end-to-end speedup on GPT-2 training (Table 1).",
        "model_card": None,
    },
    "DPO (2305.18290)": {
        "paper": "2305.18290",
        "repo": "https://github.com/eric-mitchell/direct-preference-optimization",
        "repo_relation": "official author implementation",
        "benchmark": "Reproduce DPO on IMDB sentiment vs PPO (Section 6 win-rate).",
        "model_card": None,
    },
    "Mamba (2312.00752)": {
        "paper": "2312.00752",
        "repo": "https://github.com/state-spaces/mamba",
        "repo_relation": "official author/lab implementation",
        "benchmark": "Reproduce Mamba on Pile language modeling perplexity (Table 4).",
        "model_card": None,
    },
}

RELATED_WORKS = {
    "2201.11903": [
        {
            "title": "Self-Consistency Improves Chain of Thought Reasoning in Language Models",
            "year": "2022",
            "url": "https://arxiv.org/abs/2203.11171",
            "note": "Samples multiple reasoning paths and chooses the consensus answer, often improving over single CoT traces.",
        },
        {
            "title": "Large Language Models are Zero-Shot Reasoners",
            "year": "2022",
            "url": "https://arxiv.org/abs/2205.11916",
            "note": "Shows that a trigger such as 'Let's think step by step' can elicit reasoning without hand-written exemplars.",
        },
        {
            "title": "Automatic Chain of Thought Prompting in Large Language Models",
            "year": "2022",
            "url": "https://arxiv.org/abs/2210.03493",
            "note": "Automates demonstration construction instead of relying on manually authored CoT examples.",
        },
        {
            "title": "ReAct: Synergizing Reasoning and Acting in Language Models",
            "year": "2022",
            "url": "https://arxiv.org/abs/2210.03629",
            "note": "Combines reasoning traces with tool/action steps, moving beyond pure answer-only prompting.",
        },
        {
            "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
            "year": "2023",
            "url": "https://arxiv.org/abs/2305.10601",
            "note": "Generalizes linear CoT into search over multiple reasoning branches.",
        },
        {
            "title": "Reasoning-model era",
            "year": "2024-2026",
            "url": "https://openai.com/index/learning-to-reason-with-llms/",
            "note": "Modern reasoning-trained models and test-time compute often eclipse manual few-shot CoT on hard math/code tasks, while still inheriting the core idea that intermediate reasoning can improve outcomes.",
        },
    ]
}

with st.sidebar:
    st.header("Repro Audit")
    st.caption(
        "A pre-flight system for deciding whether a paper is worth reproducing before "
        "spending researcher time or accelerator budget."
    )
    st.divider()
    st.subheader("What the report means")
    st.markdown(
        "- **Claims** are measurable paper results.\n"
        "- **Gaps** are missing details that could block reproduction.\n"
        "- **Links** are repo files likely to implement or evaluate each claim.\n"
        "- **Feasibility** is a triage verdict, not a guarantee."
    )
    st.divider()
    with st.expander("Model routes", expanded=False):
        st.caption(
            "Premium reasoning routes are ON because RC_PREMIUM_MODELS=1."
            if USE_PREMIUM_MODELS
            else "Standard faster/lower-cost routes are active. Set RC_PREMIUM_MODELS=1 only for a few higher-quality runs."
        )
        for role, models in MODEL_ROUTES.items():
            st.markdown(f"**{role}** → `{models[0]}`")
        st.caption("Routes fail over on unavailable or rate-limited models.")

st.markdown(
    """
    <div class="run-panel">
      <h2>Run an audit</h2>
      <p>
        Paste a paper link and describe what you want to build or reproduce. The app
        searches for a likely implementation repository, audits the paper and code,
        then turns missing details into concrete build steps and follow-up questions.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

pick = st.selectbox("Case study", list(examples.keys()), index=0)
preset = examples[pick] or {}

input_col, target_col = st.columns([1, 1])
with input_col:
    paper = st.text_input(
        "Paper link or arXiv id",
        value=preset.get("paper", ""),
        help="arXiv id, arXiv URL, local PDF, or local text file.",
    )
    st.caption(
        "For known papers, the app uses the benchmark registry. For new arXiv papers, "
        "it searches GitHub by arXiv id, title, and author/title terms."
    )
with target_col:
    benchmark = st.text_area(
        "What are you trying to build or reproduce?",
        value=preset.get("benchmark", ""),
        help="A product use case, API behavior, result, table, figure, metric, or experiment you care about.",
        height=116,
    )

option_col, action_col = st.columns([1.25, 1])
with option_col:
    with st.expander("Optional context and actions", expanded=False):
        model_card = st.text_input(
            "Model card or supplementary URL",
            value=preset.get("model_card", "") or "",
            help="File path or HuggingFace URL.",
        )
        reviews = st.text_input(
            "OpenReview URL",
            value=preset.get("reviews", "") or "",
            help="Reviewer comments can expose underspecified details.",
        )
        author_email = st.text_input(
            "Author email",
            value="",
            help="Used only to open a prefilled mail draft after the audit.",
        )
        repo_override = st.text_input(
            "Repository override",
            value="",
            help="Optional. Use this if discovery picks the wrong repo or you already know the implementation.",
        )
        use_retrieval = st.checkbox("Use local embedding retrieval over the repo", value=True)
with action_col:
    st.markdown(
        """
        <div class="copy-block">
          <h3>Output</h3>
          <p>
            The report produces an implementation center, author contacts, a
            repository health check, expected first commands, claim-to-code links,
            missing-detail questions, raw JSON, and tailored author emails.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    run_button = st.button("Run audit", type="primary", width="stretch")


# ---------- Render helpers ----------
def feasibility_badge(value: str) -> str:
    cls = f"feasibility-{value}"
    return f'<span class="{cls}">{value.upper()}</span>'


def severity_class(value: str) -> str:
    return f"severity-{value}"


def _is_url(value: str | None) -> bool:
    return bool(value and value.startswith(("http://", "https://")))


def _arxiv_id(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    if "arxiv.org" in text:
        tail = text.rstrip("/").split("/")[-1]
        return tail.replace(".pdf", "")
    parts = text.split("/")
    candidate = parts[-1]
    if candidate.count(".") == 1 and candidate.replace(".", "").isdigit():
        return candidate
    return None


def _known_case_for_paper(value: str | None) -> dict | None:
    arxiv_id = _arxiv_id(value)
    if not arxiv_id:
        return None
    for item in examples.values():
        if item and _arxiv_id(item.get("paper")) == arxiv_id:
            return item
    return None


def _fetch_arxiv_metadata(arxiv_id: str) -> dict:
    url = "http://export.arxiv.org/api/query"
    try:
        response = httpx.get(url, params={"id_list": arxiv_id}, timeout=12.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return {}
    text = response.text
    title_match = re.search(r"<entry>.*?<title>(.*?)</title>", text, flags=re.DOTALL)
    authors = re.findall(r"<author>\s*<name>(.*?)</name>", text)
    summary_match = re.search(r"<entry>.*?<summary>(.*?)</summary>", text, flags=re.DOTALL)
    published_match = re.search(r"<entry>.*?<published>(.*?)</published>", text, flags=re.DOTALL)
    updated_match = re.search(r"<entry>.*?<updated>(.*?)</updated>", text, flags=re.DOTALL)
    return {
        "title": " ".join(title_match.group(1).split()) if title_match else "",
        "authors": [" ".join(a.split()) for a in authors],
        "summary": " ".join(summary_match.group(1).split()) if summary_match else "",
        "published": published_match.group(1).strip() if published_match else "",
        "updated": updated_match.group(1).strip() if updated_match else "",
    }


def _github_repo_search(query: str, *, limit: int = 5) -> list[dict]:
    if not query.strip():
        return []
    try:
        response = httpx.get(
            "https://api.github.com/search/repositories",
            params={
                "q": f"{query} in:name,description,readme",
                "sort": "stars",
                "order": "desc",
                "per_page": limit,
            },
            headers={"Accept": "application/vnd.github+json"},
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        return []
    return [item for item in data.get("items", []) if isinstance(item, dict)]


def _score_repo_candidate(item: dict, *, arxiv_id: str, title: str, authors: list[str]) -> float:
    haystack = " ".join(
        str(item.get(key) or "")
        for key in ("full_name", "name", "description", "html_url")
    ).lower()
    title_tokens = [t for t in re.findall(r"[a-z0-9]+", title.lower()) if len(t) > 3]
    author_tokens = [
        t
        for author in authors[:3]
        for t in re.findall(r"[a-z0-9]+", author.lower())
        if len(t) > 3
    ]
    score = 0.0
    if arxiv_id and arxiv_id in haystack:
        score += 8.0
    if title_tokens:
        overlap = sum(1 for token in title_tokens if token in haystack)
        score += 5.0 * overlap / max(1, len(title_tokens))
    if "chain" in title.lower() and "thought" in title.lower():
        if "chain-of-thought" in haystack or "chain_of_thought" in haystack:
            score += 3.0
        if re.search(r"\bcot\b", haystack):
            score += 1.5
        if "gsm8k" in haystack:
            score += 1.0
    acronym = "".join(token[0] for token in title_tokens[:6])
    if len(acronym) >= 3 and acronym in haystack:
        score += 1.0
    if author_tokens:
        overlap = sum(1 for token in author_tokens if token in haystack)
        score += 2.0 * overlap / max(1, len(author_tokens))
    score += min(float(item.get("stargazers_count") or 0), 5000.0) / 5000.0
    if item.get("fork"):
        score -= 1.0
    return score


def _repo_relation_for_candidate(item: dict, *, authors: list[str]) -> str:
    haystack = " ".join(
        str(item.get(key) or "")
        for key in ("full_name", "name", "description", "html_url")
    ).lower()
    owner = str(item.get("owner", {}).get("login", "")).lower()
    if "official" in haystack:
        return "likely official implementation"
    author_tokens = {
        token
        for author in authors[:4]
        for token in re.findall(r"[a-z0-9]+", author.lower())
        if len(token) > 3
    }
    if author_tokens and any(token in owner for token in author_tokens):
        return "likely author implementation"
    if any(word in haystack for word in ("implementation", "reproduction", "replication", "reproduce")):
        return "unofficial or third-party implementation"
    return "repository relation uncertain"


def discover_repo_for_paper(paper_input: str | None) -> tuple[str | None, str, list[dict], str]:
    known = _known_case_for_paper(paper_input)
    if known and known.get("repo"):
        return str(known["repo"]), "benchmark registry", [], known.get("repo_relation", "registered implementation")

    arxiv_id = _arxiv_id(paper_input)
    if not arxiv_id:
        return None, "no arXiv id detected", [], "unknown"

    metadata = _fetch_arxiv_metadata(arxiv_id)
    title = metadata.get("title", "")
    authors = metadata.get("authors", [])
    queries = [arxiv_id]
    if title:
        queries.append(title)
        title_tokens = re.findall(r"[A-Za-z0-9]+", title)
        queries.append(" ".join(title_tokens[:6]))
        if "chain" in title.lower() and "thought" in title.lower():
            queries.extend([
                "chain-of-thought prompting",
                "chain of thought hub GSM8K",
                "cot prompting GSM8K",
                "chain-of-thought reproduction",
            ])
        method_terms = [
            token
            for token in title_tokens
            if len(token) > 4 and token.lower() not in {"large", "language", "models", "prompting", "elicits"}
        ]
        if method_terms:
            queries.append(" ".join(method_terms[:4]))
    if authors and title:
        queries.append(f"{authors[0]} {' '.join(re.findall(r'[A-Za-z0-9]+', title)[:4])}")

    candidates_by_url: dict[str, dict] = {}
    for query in queries:
        for item in _github_repo_search(query):
            url = item.get("html_url")
            if isinstance(url, str):
                candidates_by_url[url] = item

    scored = sorted(
        (
            {
                "url": url,
                "name": item.get("full_name", url),
                "description": item.get("description") or "",
                "stars": item.get("stargazers_count") or 0,
                "relation": _repo_relation_for_candidate(item, authors=authors),
                "score": _score_repo_candidate(
                    item,
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                ),
            }
            for url, item in candidates_by_url.items()
        ),
        key=lambda item: item["score"],
        reverse=True,
    )
    if not scored or scored[0]["score"] < 1.2:
        return None, "GitHub search found no high-confidence implementation", scored[:5], "none found"
    return scored[0]["url"], "GitHub repository search", scored[:5], scored[0]["relation"]


def _paper_link(report: AuditReport, paper_input: str | None) -> str | None:
    paper_id = report.paper_id or _arxiv_id(paper_input)
    if paper_id:
        return f"https://arxiv.org/abs/{paper_id}"
    if _is_url(paper_input):
        return paper_input
    return None


def _repo_link(repo_input: str | None) -> str | None:
    if _is_url(repo_input) and "github.com" in repo_input.lower():
        return repo_input.rstrip("/").removesuffix(".git")
    return None


def _github_blob_link(repo_input: str | None, path: str) -> str | None:
    base = _repo_link(repo_input)
    if not base:
        return None
    return f"{base}/blob/main/{quote(path)}"


def _anchor(label: str, href: str, *, primary: bool = False, dark: bool = False) -> str:
    cls = "action-link"
    if primary:
        cls += " primary"
    if dark:
        cls += " dark"
    return f'<a class="{cls}" href="{escape(href)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>'


def _email_draft(report: AuditReport) -> tuple[str, str]:
    title = report.paper_title or report.paper_id or "your paper"
    subject = f"Reproducibility question about {title}"
    headline = next((c for c in report.claims if c.claim.is_main_claim), report.claims[0] if report.claims else None)
    blockers = []
    for claim_audit in report.claims:
        blockers.extend(claim_audit.blockers)
    blockers.extend(m.description for m in report.overall_missing if m.severity in {"high", "medium"})
    blockers = blockers[:5]
    next_steps = report.next_steps[:3]

    lines = [
        "Hi,",
        "",
        f"I'm trying to reproduce the result described as: {report.benchmark}",
    ]
    if headline:
        lines.extend([
            "",
            f"The main claim I am targeting is: {headline.claim.statement}",
        ])
    if blockers:
        lines.extend(["", "The audit surfaced a few details I could not confidently resolve:"])
        lines.extend(f"- {item}" for item in blockers)
    if next_steps:
        lines.extend(["", "Would you recommend starting with any of these steps?"])
        lines.extend(f"- {step}" for step in next_steps)
    lines.extend([
        "",
        "Any pointers to the intended command, config, checkpoint, or evaluation script would help a lot.",
        "",
        "Thanks,",
    ])
    return subject, "\n".join(lines)


def _authors_label(report: AuditReport) -> str:
    if not report.paper_authors:
        return "No authors detected from metadata."
    authors = report.paper_authors[:4]
    suffix = "" if len(report.paper_authors) <= 4 else f" +{len(report.paper_authors) - 4} more"
    return ", ".join(authors) + suffix


def render_author_panel(report: AuditReport, author_email: str | None) -> None:
    st.markdown("### Authors and contact")
    st.markdown(
        f"""
        <div class="copy-block">
          <p><b>Detected authors:</b> {escape(_authors_label(report))}</p>
          <p>
            arXiv usually exposes author names reliably, but email addresses are not
            always machine-readable. Add an address in the optional field to prefill
            the mail draft; otherwise the app still gives you the message body.
          </p>
          <p><b>Email target:</b> {escape(author_email or "not set")}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_arxiv_date(value: str) -> str:
    if not value:
        return "unknown"
    return value.split("T", 1)[0]


def render_paper_context(report: AuditReport, paper_input: str | None) -> None:
    arxiv_id = report.paper_id or _arxiv_id(paper_input)
    metadata = _fetch_arxiv_metadata(arxiv_id) if arxiv_id else {}
    title = report.paper_title or metadata.get("title") or arxiv_id or "Paper"
    published = _format_arxiv_date(metadata.get("published", ""))
    updated = _format_arxiv_date(metadata.get("updated", ""))
    st.markdown("### Paper context")
    st.markdown(
        f"""
        <div class="copy-block">
          <p><b>Paper:</b> {escape(title)}</p>
          <p><b>arXiv id:</b> {escape(arxiv_id or "unknown")}</p>
          <p><b>First posted:</b> {escape(published)}</p>
          <p><b>Last metadata update:</b> {escape(updated)}</p>
          <p>
            This context helps interpret reproducibility. Older papers may have
            been superseded by stronger methods, newer model families, better
            benchmark harnesses, or public replications that are easier to run
            than the original experimental setup.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    related = RELATED_WORKS.get(arxiv_id or "")
    if related:
        st.markdown("**Later work and possible replacements**")
        for item in related:
            st.markdown(
                f"""
                <div class="code-link">
                  <b><a href="{escape(item["url"])}" target="_blank" rel="noopener noreferrer">{escape(item["title"])}</a></b>
                  <span class="small-muted">({escape(item["year"])})</span><br>
                  <span class="small-muted">{escape(item["note"])}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def expected_commands(report: AuditReport) -> list[tuple[str, str, str]]:
    rs = report.repo_summary
    if not rs.exists:
        return []
    commands: list[tuple[str, str, str]] = []
    deps = set(rs.dependency_files)
    if "requirements.txt" in deps:
        commands.append(("Install dependencies", "pip install -r requirements.txt", "requirements.txt detected."))
    if "pyproject.toml" in deps or "setup.py" in deps:
        commands.append(("Install package", "pip install -e .", "Python package metadata detected."))
    if "environment.yml" in deps:
        commands.append(("Create conda env", "conda env create -f environment.yml", "Conda environment file detected."))
    entry = best_entry_script(report)
    if entry:
        commands.append(("Run likely entry point", f"python {entry}", "Inferred from repository file names and excerpts."))
        if rs.likely_config_files:
            commands.append(
                (
                    "Try entry point with config",
                    f"python {entry} --config {rs.likely_config_files[0]}",
                    "Config flag is a guess; inspect script args before running.",
                )
            )
    eval_script = next(
        (
            script
            for script in rs.likely_eval_scripts
            if script != entry and _repo_file_exists(report, script) and _file_line_count(report, script) > 5
        ),
        None,
    )
    if eval_script:
        commands.append(
            (
                "Run likely evaluation",
                f"python {eval_script}",
                "Evaluation script inferred from repo structure.",
            )
        )
    return commands


def _report_text(report: AuditReport) -> str:
    parts = [
        report.paper_id or "",
        report.paper_title or "",
        report.benchmark or "",
        report.repo_summary.path or "",
    ]
    return " ".join(parts).lower()


def is_cot_case(report: AuditReport) -> bool:
    text = _report_text(report)
    return any(term in text for term in ["2201.11903", "chain-of-thought", "chain of thought", "gsm8k", "cot"])


def is_speculative_case(report: AuditReport) -> bool:
    text = _report_text(report)
    return any(term in text for term in ["2211.17192", "speculative decoding", "speculative-decoding", "speculative_generate"])


def _file_line_count(report: AuditReport, rel_path: str) -> int:
    return len(_read_repo_lines(report, rel_path))


def best_entry_script(report: AuditReport) -> str | None:
    benchmark = report.benchmark.lower()
    preferred: list[str] = []
    if is_speculative_case(report):
        preferred.extend([
            "infer.py",
            "sampling/speculative_decoding.py",
        ])
    if is_cot_case(report):
        preferred.extend([
            "gsm8k/run_gsm8k_claude_instant.py",
            "BBH/run_bbh_gpt_3.5_turbo.py",
        ])
    if "bbh" in benchmark:
        preferred.insert(0, "BBH/run_bbh_gpt_3.5_turbo.py")
    preferred.extend(report.repo_summary.likely_entry_points)
    preferred.extend(report.repo_summary.likely_eval_scripts)
    seen: set[str] = set()
    for path in preferred:
        if path in seen:
            continue
        seen.add(path)
        if _repo_file_exists(report, path) and _file_line_count(report, path) > 5:
            return path
    return None


def render_expected_commands(report: AuditReport) -> None:
    st.markdown("### Expected first commands")
    commands = expected_commands(report)
    if not commands:
        st.markdown(
            """
            <div class="copy-block">
              <p>
                No runnable command can be proposed because no repository was found
                or the repository did not expose obvious entry/evaluation scripts.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    st.markdown(
        """
        <div class="copy-block">
          <p>
            These are not executed by the app. They are likely first commands a human
            would inspect before creating a controlled smoke test.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for label, command, rationale in commands:
        st.markdown(f"**{label}**")
        st.code(command, language="bash")
        st.caption(rationale)


def _repo_root(report: AuditReport) -> Path | None:
    if not report.repo_summary.exists:
        return None
    root = Path(report.repo_summary.path)
    return root if root.exists() else None


def _read_repo_lines(report: AuditReport, rel_path: str) -> list[str]:
    root = _repo_root(report)
    if root is None:
        return []
    path = (root / rel_path).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return []
    if not path.exists() or not path.is_file():
        return []
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []


def _repo_file_exists(report: AuditReport, rel_path: str) -> bool:
    root = _repo_root(report)
    if root is None:
        return False
    return (root / rel_path).exists()


def _line_anchor(
    report: AuditReport,
    *,
    rel_path: str,
    label: str,
    patterns: list[str],
    why: str,
    change: str,
    window: int = 2,
) -> dict | None:
    lines = _read_repo_lines(report, rel_path)
    if not lines:
        return None
    match_idx = 0
    for pattern in patterns:
        regex = re.compile(pattern, re.IGNORECASE)
        found = next((i for i, line in enumerate(lines) if regex.search(line)), None)
        if found is not None:
            match_idx = found
            break
    start = max(0, match_idx - window)
    end = min(len(lines), match_idx + window + 1)
    snippet = "\n".join(f"{i + 1:>4}  {lines[i]}" for i in range(start, end))
    return {
        "path": rel_path,
        "line": match_idx + 1,
        "range": f"{start + 1}-{end}",
        "label": label,
        "why": why,
        "change": change,
        "snippet": snippet,
    }


def code_anchors(report: AuditReport) -> list[dict]:
    benchmark = report.benchmark.lower()
    paths: list[str] = []
    for claim_audit in report.claims:
        for link in sorted(claim_audit.code_links, key=lambda item: item.confidence, reverse=True):
            paths.append(link.path)
    paths.extend(report.repo_summary.likely_entry_points)
    paths.extend(report.repo_summary.likely_eval_scripts)
    if is_speculative_case(report):
        paths.extend([
            "infer.py",
            "sampling/speculative_decoding.py",
            "sampling/codec_speculative_decoding.py",
            "utils/logits_processor.py",
            "README.md",
            "requirements.txt",
        ])
    if is_cot_case(report):
        paths.extend([
            "gsm8k/run_gsm8k_claude_instant.py",
            "gsm8k/lib_prompt/prompt_original.txt",
            "readme.md",
        ])
    if "bbh" in benchmark:
        paths.extend([
            "BBH/run_bbh_gpt_3.5_turbo.py",
            "BBH/lib_prompt/boolean_expressions.txt",
        ])

    seen: set[str] = set()
    unique_paths = []
    for path in paths:
        if path and path not in seen and _repo_file_exists(report, path):
            unique_paths.append(path)
            seen.add(path)

    anchors: list[dict] = []
    if is_speculative_case(report):
        anchors.extend([
            _line_anchor(
                report,
                rel_path="README.md",
                label="Minimal model contract",
                patterns=[r"Here are some requirements", r"drafter model must share", r"target model should be large"],
                why="This states the reproduction-critical assumption: a large target model and smaller drafter must share compatible tokenization.",
                change="Pick an accessible target/drafter pair first, then treat exact paper speedups as secondary until the pair is stable.",
                window=2,
            ),
            _line_anchor(
                report,
                rel_path="infer.py",
                label="Target and drafter setup",
                patterns=[r"target_model\s*=", r"drafter_model\s*=", r"AutoModelForCausalLM\.from_pretrained"],
                why="These lines choose the two models whose latency ratio determines whether speculative decoding can help.",
                change="Replace the hard-coded Llama defaults with your target model, a smaller drafter, device placement, and quantization policy.",
                window=6,
            ),
            _line_anchor(
                report,
                rel_path="infer.py",
                label="Generation knobs",
                patterns=[r"self\.gamma", r"self\.gen_len", r"self\.processor", r"/gamma"],
                why="Gamma, generation length, cache usage, and sampling policy are the knobs that control the speed/quality tradeoff.",
                change="Expose gamma, cache, max tokens, and decoding mode as experiment parameters before recording any speedup claim.",
                window=3,
            ),
            _line_anchor(
                report,
                rel_path="infer.py",
                label="Speculative call and acceptance metric",
                patterns=[r"speculative_generate\(", r"accept_rate", r"Acceptance rate"],
                why="This is the runnable bridge from the CLI into the algorithm, and it returns the acceptance rate needed to diagnose speedups.",
                change="Wrap this call in a batchable function that logs prompt length, output length, gamma, acceptance rate, wall time, and hardware.",
                window=4,
            ),
            _line_anchor(
                report,
                rel_path="infer.py",
                label="Autoregressive baseline",
                patterns=[r"autoregressive_generate\(", r"Target AR", r"base_throughput"],
                why="A reproducer needs this baseline because the paper claim is a speedup over ordinary target-model decoding.",
                change="Run this with the same prompts, target model, tokenizer, cache setting, and sampling processor as speculative decoding.",
                window=4,
            ),
            _line_anchor(
                report,
                rel_path="infer.py",
                label="Throughput reporting",
                patterns=[r"spec_throughput / base_throughput", r"Throughput increase", r"spec_throughput"],
                why="These lines define the visible demo metric, but the current calculation is interactive and should be standardized for experiments.",
                change="Move timing into a fixed benchmark script that reports tokens/sec, latency per request, acceptance rate, and confidence intervals.",
                window=3,
            ),
            _line_anchor(
                report,
                rel_path="sampling/speculative_decoding.py",
                label="Core algorithm signature",
                patterns=[r"def speculative_generate", r"gamma: int", r"max_gen_len"],
                why="This function is the smallest reusable implementation surface for a product or reproducer.",
                change="Import this function directly from a benchmark harness instead of driving reproduction through the interactive CLI.",
                window=4,
            ),
            _line_anchor(
                report,
                rel_path="sampling/speculative_decoding.py",
                label="Drafter proposes gamma tokens",
                patterns=[r"for _ in range\(gamma\)", r"draft_probs", r"draft_tokens"],
                why="This is the speculative part: the smaller model proposes multiple future tokens before the target model verifies them.",
                change="Instrument this block to log drafter time separately from target verification time.",
                window=4,
            ),
            _line_anchor(
                report,
                rel_path="sampling/speculative_decoding.py",
                label="Target verifies and rejects",
                patterns=[r"rejection sampling", r"fractions = p / q", r"r\[i\] > fractions", r"drafts_accepted"],
                why="These lines enforce distribution preservation by rejecting drafts that the target model would not support.",
                change="Keep this logic unchanged for correctness tests; only optimize tensor shapes/cache behavior around it.",
                window=5,
            ),
            _line_anchor(
                report,
                rel_path="utils/logits_processor.py",
                label="Sampling policy",
                patterns=[r"class GreedyProcessor", r"class MultinomialProcessor", r"class TopKProcessor", r"class NucleusProcessor"],
                why="Speculative decoding must use compatible sampling behavior for target and drafter comparisons.",
                change="Fix one processor for all baselines in a reproduction table; changing top-k/top-p changes the experiment.",
                window=3,
            ),
        ])

    if is_cot_case(report):
        anchors.extend([
            _line_anchor(
                report,
                rel_path="readme.md",
                label="GSM8K run command",
                patterns=[r"python run_gsm8k_claude", r"--prompt_file=lib_prompt", r"### GSM8k"],
                why="This is the README-level command surface for a runnable CoT benchmark case.",
                change="Turn this into a one-command smoke test that accepts provider credentials and writes structured results.",
                window=2,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/lib_prompt/prompt_original.txt",
                label="Few-shot CoT exemplars",
                patterns=[r"let'?s think step by step", r"Question:", r"Answer:"],
                why="These demonstrations are the actual method: the model sees worked reasoning traces before answering.",
                change="Keep these examples for benchmark reproduction, then create a separate product prompt with the same reasoning pattern.",
                window=5,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/run_gsm8k_claude_instant.py",
                label="CLI controls",
                patterns=[r"parser\.add_argument", r"--prompt_file", r"--output_file"],
                why="These arguments expose the prompt file, API key, model engine, eval mode, and output path.",
                change="Make these explicit UI or config fields so a user can rerun the same experiment without editing code.",
                window=3,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/run_gsm8k_claude_instant.py",
                label="GSM8K data loading",
                patterns=[r"load_dataset\('gsm8k'", r"validation_index", r"gsm8k_test"],
                why="This is where the reproduction chooses the benchmark split and validation subset.",
                change="Freeze the exact split in logs; for product use, replace this with user-like arithmetic tasks.",
                window=3,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/run_gsm8k_claude_instant.py",
                label="Prompt assembly",
                patterns=[r"claude_prompt =", r"open\(args\.prompt_file", r"prompt_q"],
                why="This joins the few-shot CoT exemplars with the current question, which is the heart of the implementation.",
                change="Factor this into build_cot_prompt(question, exemplars) and add a no-CoT baseline prompt beside it.",
                window=3,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/run_gsm8k_claude_instant.py",
                label="Model/API call",
                patterns=[r"client\.completion", r"max_tokens_to_sample", r"temperature"],
                why="This is the replaceable backend call; the original paper used PaLM, this repo uses an Anthropic endpoint.",
                change="Make provider, model, temperature, and max tokens configurable, and record them in every result row.",
                window=4,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/run_gsm8k_claude_instant.py",
                label="Answer parsing and accuracy",
                patterns=[r"print\(['\"]Accuracy", r"ans_ ==", r"correct / total"],
                why="This converts generated reasoning into the exact-answer metric used for the benchmark.",
                change="Keep exact match for GSM8K reproduction, but add product metrics such as refusal rate, latency, and human review tags.",
                window=5,
            ),
            _line_anchor(
                report,
                rel_path="gsm8k/run_gsm8k_claude_instant.py",
                label="Result logging",
                patterns=[r"f\.write", r"with open\(args\.output_file", r"output_file"],
                why="This is where outputs become inspectable evidence instead of an ephemeral terminal demo.",
                change="Write JSONL with question, prompt mode, model, raw output, parsed answer, gold answer, and correctness.",
                window=4,
            ),
        ])

    for path in unique_paths[:10]:
        lower = path.lower()
        if lower.endswith((".txt", ".chatml")) and "prompt" in lower:
            anchors.append(
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Prompt template / examples",
                    patterns=[r"let'?s think step by step", r"question:", r"answer"],
                    why="This is the few-shot or zero-shot prompt format that actually implements the paper idea.",
                    change="Replace or adapt these demonstrations for your product task; keep a baseline direct-answer prompt for comparison.",
                    window=3,
                )
            )
            continue
        if lower.endswith((".md", ".txt")):
            anchors.append(
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Run instructions / benchmark framing",
                    patterns=[r"### GSM8k", r"python run_gsm8k", r"### BBH", r"## Run", r"source of numbers", r"gsm8k"],
                    why="This tells you what the repository claims to run and where benchmark numbers come from.",
                    change="Use this to decide whether you are implementing the paper, a benchmark harness, or a third-party evaluation.",
                    window=1,
                )
            )
            continue
        if lower.endswith(".py"):
            anchors.extend([
                _line_anchor(
                    report,
                    rel_path=path,
                    label="CLI controls",
                    patterns=[r"parser\.add_argument", r"add_argument"],
                    why="These arguments are the knobs you can expose in a prototype or small internal tool.",
                    change="Rename the knobs around your app use case: model, prompt file, output path, task, and evaluation mode.",
                ),
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Data loading",
                    patterns=[r"=\s*load_dataset", r"json\.load", r"data/%s", r"open\(.*data", r"load_dataset"],
                    why="This is where the benchmark examples enter the program.",
                    change="Replace this with your product inputs, or keep it only for validation tests.",
                ),
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Prompt assembly",
                    patterns=[r"claude_prompt", r"prompt_q", r"open\(args\.prompt_file", r"let'?s think step by step", r"lib_prompt", r"prompt_file"],
                    why="This is the core CoT implementation surface: examples plus the user's question become the model prompt.",
                    change="Factor this into a pure function like build_prompt(question, examples, mode).",
                ),
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Model/API call",
                    patterns=[r"ChatCompletion", r"client\.completion", r"completion_with_backoff", r"temperature", r"model="],
                    why="This is the call you would swap to your own model provider or local inference backend.",
                    change="Make provider/model/temperature/max tokens configurable and add retry/error handling around it.",
                ),
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Answer parsing / metric",
                    patterns=[r"print\(['\"]Accuracy", r"reference_answer", r"ans_ ==", r"extract_ans", r"parse_answer", r"accuracy"],
                    why="This defines what counts as success, which is different for a product than for a benchmark paper.",
                    change="Replace exact-answer parsing with your app's acceptance criteria, logging both raw reasoning and final answer.",
                ),
                _line_anchor(
                    report,
                    rel_path=path,
                    label="Output artifact",
                    patterns=[r"with open\(args\.output_file", r"f\.write", r"fd\.write", r"outputs/", r"output_file", r"with open"],
                    why="This is where results are stored for review and debugging.",
                    change="Write structured JSON/CSV records instead of free-form text so product regressions are trackable.",
                ),
            ])

    clean = [anchor for anchor in anchors if anchor is not None]
    deduped: list[dict] = []
    keys: set[tuple[str, str, int]] = set()
    for anchor in clean:
        key = (anchor["path"], anchor["label"], anchor["line"])
        if key not in keys:
            deduped.append(anchor)
            keys.add(key)
    return deduped[:14]


def render_code_anchors(report: AuditReport, *, repo_input: str | None) -> None:
    st.markdown("### Code map")
    anchors = code_anchors(report)
    if not anchors:
        st.markdown(
            """
            <div class="copy-block">
              <p>
                No line-level code anchors were found. This usually means no repository
                was available or the implementation is mostly notebooks/binary assets.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    st.markdown(
        """
        <div class="copy-block">
          <p>
            These are concrete implementation anchors from the selected repository.
            Use them as the first files and line ranges to inspect before building
            a wrapper, demo, or product integration.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for anchor in anchors:
        href = _github_blob_link(repo_input, anchor["path"])
        title = f'{anchor["path"]}:{anchor["range"]}'
        if href:
            title_html = f'<a href="{escape(href)}" target="_blank" rel="noopener noreferrer">{escape(title)}</a>'
        else:
            title_html = escape(title)
        st.markdown(
            f"""
            <div class="anchor-card">
              <div class="anchor-meta">{escape(anchor["label"])}</div>
              <h4>{title_html}</h4>
              <p><b>Why it matters:</b> {escape(anchor["why"])}</p>
              <p><b>Implementation move:</b> {escape(anchor["change"])}</p>
              <div class="snippet">{escape(anchor["snippet"])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def repo_health_rows(report: AuditReport) -> list[dict]:
    rs = report.repo_summary
    return [
        {"Check": "Repository found", "Status": "pass" if rs.exists else "missing", "Evidence": rs.path},
        {"Check": "README present", "Status": "pass" if any(f.lower().startswith("readme") for f in rs.important_files) else "missing", "Evidence": ", ".join(rs.important_files)},
        {"Check": "Dependencies present", "Status": "pass" if rs.dependency_files else "missing", "Evidence": ", ".join(rs.dependency_files)},
        {"Check": "Entry point found", "Status": "pass" if rs.likely_entry_points else "missing", "Evidence": ", ".join(rs.likely_entry_points)},
        {"Check": "Evaluation script found", "Status": "pass" if rs.likely_eval_scripts else "missing", "Evidence": ", ".join(rs.likely_eval_scripts)},
        {"Check": "Configs found", "Status": "pass" if rs.likely_config_files else "missing", "Evidence": ", ".join(rs.likely_config_files)},
        {"Check": "Tests found", "Status": "pass" if rs.has_tests else "missing", "Evidence": "test files detected" if rs.has_tests else ""},
        {"Check": "Code links produced", "Status": "pass" if sum(len(c.code_links) for c in report.claims) else "missing", "Evidence": str(sum(len(c.code_links) for c in report.claims))},
    ]


def render_repo_health(report: AuditReport) -> None:
    st.markdown("### Repository health")
    st.markdown(
        """
        <div class="copy-block">
          <p>
            This is a quick implementation-readiness checklist. Missing items do not
            prove the paper is irreproducible, but they tell you where a reproduction
            attempt will probably stall.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.dataframe(repo_health_rows(report), width="stretch", hide_index=True)


def render_repo_provenance(
    *,
    repo_input: str | None,
    repo_source: str | None,
    repo_relation: str | None,
    discovery_candidates: list[dict] | None,
) -> None:
    st.markdown("### Implementation provenance")
    relation = repo_relation or "unknown"
    source = repo_source or "not recorded"
    repo_display = repo_input or "(none)"
    st.markdown(
        f"""
        <div class="copy-block">
          <p><b>Selected repo:</b> {escape(repo_display)}</p>
          <p><b>Discovery source:</b> {escape(source)}</p>
          <p><b>Relationship to paper:</b> {escape(relation)}</p>
          <p>
            Official author repositories are stronger evidence than third-party
            replications. Unofficial repos can still be useful for algorithmic
            smoke tests, but they should not be treated as proof that the original
            paper's exact setup is reproducible.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if discovery_candidates:
        st.markdown("**Other repository candidates considered**")
        st.dataframe(discovery_candidates, width="stretch", hide_index=True)


def ask_options(report: AuditReport) -> list[dict]:
    options: list[dict] = []
    for idx, missing in enumerate(report.overall_missing):
        options.append(
            {
                "kind": "missing",
                "label": f"{missing.severity} {missing.category}: {missing.description[:90]}",
                "category": missing.category,
                "severity": missing.severity,
                "description": missing.description,
            }
        )
    for claim_idx, claim_audit in enumerate(report.claims, start=1):
        for blocker in claim_audit.blockers:
            options.append(
                {
                    "kind": "blocker",
                    "label": f"claim {claim_idx} blocker: {blocker[:90]}",
                    "category": "claim_blocker",
                    "severity": claim_audit.feasibility,
                    "description": blocker,
                }
            )
    return options


SOURCING_CATEGORIES = {
    "checkpoint",
    "data_preprocessing",
    "data_split",
    "hardware",
    "hyperparameters",
    "compute_budget",
    "dependencies",
    "model_architecture",
    "dataset_details",
    "random_seed",
    "training_recipe",
}


def is_true_blocker_gap(item: MissingDetail | dict) -> bool:
    category = item.category if isinstance(item, MissingDetail) else item.get("category", "")
    severity = item.severity if isinstance(item, MissingDetail) else item.get("severity", "")
    description = item.description if isinstance(item, MissingDetail) else item.get("description", "")
    text = str(description).lower()
    hard_words = [
        "private",
        "proprietary",
        "unreleased",
        "internal",
        "undisclosed eval",
        "undisclosed test",
        "undisclosed dataset",
        "private dataset",
        "not named",
        "unavailable",
        "no metric",
        "metric definition",
        "secret",
    ]
    if severity != "high":
        return False
    if category in SOURCING_CATEGORIES and not any(word in text for word in hard_words):
        return False
    return True


def setup_task_count(report: AuditReport) -> int:
    return sum(
        1
        for gap in report.overall_missing
        if gap.category in SOURCING_CATEGORIES and not is_true_blocker_gap(gap)
    )


def true_blocker_count(report: AuditReport) -> int:
    return sum(1 for gap in report.overall_missing if is_true_blocker_gap(gap))


KNOWN_RESOURCE_HINTS = {
    "svamp": {
        "status": "public dataset",
        "note": "SVAMP is a public math word-problem benchmark; absence from the selected repo is a sourcing task, not a blocker.",
    },
    "gsm8k": {
        "status": "public dataset",
        "note": "GSM8K is public and commonly loaded through dataset libraries or benchmark repos.",
    },
    "mawps": {
        "status": "public dataset family",
        "note": "MAWPS-style math word-problem data can be sourced externally; exact split choices still need documentation.",
    },
    "palm": {
        "status": "model/backend sourcing",
        "note": "Treat PaLM access as a backend choice. Exact PaLM 540B historical replication may need the original service, but implementation can use an accessible strong model/API.",
    },
    "palm 540b": {
        "status": "model/backend sourcing",
        "note": "The exact 540B backend matters for matching the old paper table; it should not block implementing or evaluating the method with a modern accessible backend.",
    },
    "lamda": {
        "status": "model/backend sourcing",
        "note": "LaMDA-era exact replication may be historical/private, but comparable public or hosted model backends can support practical implementation.",
    },
    "t5": {
        "status": "public model family",
        "note": "T5 checkpoints and implementations are widely available; exact commit/checkpoint choices are experiment configuration tasks.",
    },
}


def availability_hint(text: str) -> dict | None:
    lower = text.lower()
    for key, hint in KNOWN_RESOURCE_HINTS.items():
        if key in lower:
            return hint
    if "not found within" in lower or "not present" in lower or "not in the repo" in lower:
        return {
            "status": "external artifact",
            "note": "This is missing from the selected repo, but a skilled implementer should search public datasets, model hubs, project pages, and benchmark repos before treating it as blocked.",
        }
    if any(term in lower for term in ["model", "checkpoint", "weights", "dataset", "evaluation script"]):
        return {
            "status": "sourcing task",
            "note": "This should be checked against public resources or replaced with a documented substitute before asking authors.",
        }
    return None


def claim_blocker_kind(text: str) -> str:
    hint = availability_hint(text)
    if hint:
        return hint["status"]
    if any(word in text.lower() for word in ["private", "proprietary", "unreleased", "undisclosed", "not named"]):
        return "true blocker"
    return "needs clarification"


def practical_claim_feasibility(ca: ClaimAudit) -> str:
    blockers = ca.blockers + [m.description for m in ca.missing]
    if not blockers:
        return ca.feasibility
    true_blockers = [
        item
        for item in blockers
        if claim_blocker_kind(item) == "true blocker" and not availability_hint(item)
    ]
    sourcable = [item for item in blockers if availability_hint(item)]
    statement = ca.claim.statement.lower()
    if ca.feasibility == "low" and sourcable and len(true_blockers) == 0:
        return "high"
    if ca.feasibility == "low" and "chain-of-thought" in statement and sourcable and len(true_blockers) <= 1:
        return "high"
    if ca.feasibility == "low" and ("cot" in statement or "svamp" in statement or "gsm8k" in statement) and sourcable:
        return "high"
    if ca.feasibility == "low" and sourcable and len(true_blockers) <= 1:
        return "medium"
    return ca.feasibility


def render_open_work_item(text: str, severity: str | None = None, category: str | None = None) -> None:
    hint = availability_hint(text)
    kind = hint["status"] if hint else claim_blocker_kind(text)
    prefix = f"[{severity}] " if severity else ""
    category_text = f" {category}" if category else ""
    st.markdown(
        f"- **{escape(kind)}** {escape(prefix)}{escape(category_text)} - {escape(text)}",
        unsafe_allow_html=True,
    )
    if hint:
        st.caption(hint["note"])


def question_for_gap(report: AuditReport, item: dict, use_case: str) -> tuple[str, str]:
    category = item["category"]
    description = item["description"]
    title = report.paper_title or report.paper_id or "the paper"
    ask = {
        "random_seed": "Could you share the random seeds and any deterministic settings used for this experiment?",
        "hardware": "Could you share the exact hardware setup and whether the reported number is sensitive to accelerator type or batch size?",
        "data_split": "Could you share the exact dataset split, filtering rules, and any preprocessing needed to match the reported result?",
        "hyperparameters": "Could you share the exact hyperparameters or config file used for this reported result?",
        "checkpoint": "Could you point me to the checkpoint or model weights used for the reported experiment?",
        "evaluation_script": "Could you share the evaluation command or script that computes the reported metric?",
        "training_recipe": "Could you share the training recipe, including optimizer, schedule, batch size, and stopping criteria?",
        "dataset_details": "Could you share the dataset version and any preprocessing details needed for this result?",
        "dependencies": "Could you share the intended dependency versions or environment file?",
        "code_availability": "Could you share the official implementation repository or confirm whether one exists?",
        "claim_blocker": "Could you clarify the missing implementation detail blocking this claim?",
    }.get(category, "Could you clarify this missing reproducibility detail?")

    if is_true_blocker_gap(item):
        outlook = (
            "This looks like a true blocker for exact paper-number reproduction because the "
            "detail appears undisclosed, private, or metric-defining. A practical implementation "
            "may still be possible with a documented substitute."
        )
    elif item.get("severity") == "high":
        outlook = (
            "This is a high-impact setup or comparability issue, not necessarily a stop sign. "
            "A skilled implementer can usually start by sourcing a public model/dataset/API or "
            "choosing a documented substitute, then label the result as non-exact."
        )
    else:
        outlook = (
            "This is askable and should not block progress. Start with the available repo and "
            "treat this as an assumption to validate or document."
        )

    message = (
        f"I'm trying to reproduce {title} for this use case: {use_case}\n\n"
        f"The specific blocker is: {description}\n\n"
        f"{ask}"
    )
    return message, outlook


def render_ask_panel(report: AuditReport, author_email: str | None) -> None:
    st.subheader("Ask for missing parts")
    options = ask_options(report)
    if not options:
        st.info("No missing details or blockers were recorded.")
        return
    use_case = st.text_area(
        "Use case to include in the question",
        value=report.benchmark,
        height=92,
    )
    selected = st.selectbox(
        "Missing detail or blocker",
        options,
        format_func=lambda item: item["label"],
    )
    message, outlook = question_for_gap(report, selected, use_case)
    st.markdown("**Can we replicate without this?**")
    st.markdown(f'<div class="copy-block"><p>{escape(outlook)}</p></div>', unsafe_allow_html=True)
    st.markdown("**Question to ask**")
    st.markdown(f'<div class="email-preview">{escape(message)}</div>', unsafe_allow_html=True)
    subject = f"Question about reproducing {report.paper_title or report.paper_id or 'your paper'}"
    mailto = f"mailto:{quote(author_email or '')}?subject={quote(subject)}&body={quote(message)}"
    st.markdown(
        '<div class="link-grid">' + _anchor("Open targeted email", mailto, primary=True) + "</div>",
        unsafe_allow_html=True,
    )


def _main_claim_text(report: AuditReport) -> str:
    main = next((c for c in report.claims if c.claim.is_main_claim), report.claims[0] if report.claims else None)
    return main.claim.statement if main else "No measurable paper claim was extracted."


def implementation_route(report: AuditReport, repo_relation: str | None) -> tuple[str, str]:
    relation = (repo_relation or "").lower()
    if not report.repo_summary.exists:
        return (
            "Research-only route",
            "No implementation repo is available yet. Treat the paper as design inspiration, then look for a library, author repo, or independent implementation before building.",
        )
    if is_speculative_case(report):
        return (
            "Turn the CLI into a speed benchmark",
            "Start from the target/drafter model setup, run speculative and target autoregressive decoding on identical prompts, then report throughput plus acceptance rate.",
        )
    if is_cot_case(report):
        return (
            "Implement the method, separate exact replication",
            "CoT is easy to prototype because the repo exposes prompts, GSM8K loading, API calls, and scoring; exact paper-table replication is a separate historical target because you may use a modern accessible backend instead of the original PaLM setup.",
        )
    if "official" in relation or "author" in relation:
        return (
            "Use the official path first",
            "Start from the selected repository, reproduce a tiny example, then wrap the smallest stable interface for your app.",
        )
    if "unofficial" in relation or "third-party" in relation or "replication" in relation:
        return (
            "Prototype with a third-party implementation",
            "Use the repo to learn the algorithm and validate your use case, but do not assume it matches the paper's exact experimental setup.",
        )
    return (
        "Validate repo provenance first",
        "The app found code, but its relationship to the paper is uncertain. Inspect ownership, README claims, issues, and examples before relying on it.",
    )


def practical_implementation_assessment(report: AuditReport) -> tuple[str, str]:
    anchors = code_anchors(report)
    labels = " ".join(anchor["label"].lower() for anchor in anchors)
    if is_cot_case(report):
        if all(term in labels for term in ["few-shot cot", "gsm8k data", "model/api", "answer parsing"]):
            return (
                "high",
                "The method-level path is strong: prompt exemplars, dataset loading, provider call, exact-answer scoring, and output logging are all line-anchored.",
            )
        return (
            "medium-high",
            "CoT remains practical to implement, but the current repo map is missing one or more anchors needed for a clean smoke test.",
        )
    if is_speculative_case(report):
        if all(term in labels for term in ["target and drafter", "speculative call", "autoregressive baseline", "target verifies"]):
            return (
                "high",
                "The algorithm and benchmark path are visible: model pair setup, gamma controls, speculative call, target baseline, and accept/reject logic are line-anchored. Sourcing model pairs is normal implementation work.",
            )
        return (
            "medium",
            "The repo contains runnable pieces, but the demo still needs a tighter batch benchmark around model pair, prompts, and timing.",
        )
    if report.repo_summary.exists and anchors:
        return (
            "medium",
            "The repository has line-level implementation anchors, but the app has not identified a case-specific reproduction path.",
        )
    return (
        "low",
        "No usable implementation anchors were found.",
    )


def implementation_readiness(report: AuditReport, repo_relation: str | None) -> list[dict]:
    blockers = true_blocker_count(report)
    setup_tasks = setup_task_count(report)
    commands = expected_commands(report)
    code_links = sum(len(c.code_links) for c in report.claims)
    relation = repo_relation or "unknown"
    practical_signal, practical_text = practical_implementation_assessment(report)
    return [
        {
            "Area": "Practical implementation",
            "Signal": practical_signal,
            "Interpretation": practical_text,
        },
        {
            "Area": "Exact paper reproduction",
            "Signal": report.overall_feasibility,
            "Interpretation": "This is stricter than building the method: it asks whether the original numbers can be matched with comparable settings.",
        },
        {
            "Area": "Repo provenance",
            "Signal": relation,
            "Interpretation": "Official is strongest; unofficial can be fine for prototypes but weaker for exact paper claims.",
        },
        {
            "Area": "Prototype path",
            "Signal": "available" if commands else "unclear",
            "Interpretation": "Expected commands exist." if commands else "No obvious first command was found.",
        },
        {
            "Area": "Open work",
            "Signal": f"{blockers} true blockers, {setup_tasks} sourcing tasks",
            "Interpretation": "True blockers need author/private detail. Sourcing tasks are normal SWE work: find models, datasets, hardware, or APIs and document substitutions.",
        },
        {
            "Area": "Code evidence",
            "Signal": f"{code_links} claim-code links",
            "Interpretation": "Useful implementation anchors were found." if code_links else "The implementation cannot yet be mapped to claims.",
        },
    ]


def _anchor_ref(anchor: dict | None, fallback: str) -> str:
    if not anchor:
        return fallback
    return f"`{anchor['path']}:{anchor['range']}`"


def _anchor_with_label(anchors: list[dict], text: str) -> dict | None:
    text = text.lower()
    return next((anchor for anchor in anchors if text in anchor["label"].lower()), None)


def _first_run_command(commands: list[tuple[str, str, str]], fallback: str) -> str:
    for label, command, _ in commands:
        if "run" in label.lower() or "evaluation" in label.lower():
            return command
    return commands[0][1] if commands else fallback


def implementation_steps(report: AuditReport, repo_relation: str | None) -> list[tuple[str, str]]:
    route, route_text = implementation_route(report, repo_relation)
    commands = expected_commands(report)
    anchors = code_anchors(report)
    first_anchor = anchors[0] if anchors else None
    prompt_anchor = next((a for a in anchors if "Prompt" in a["label"]), None)
    model_anchor = next((a for a in anchors if "Model" in a["label"]), None)
    metric_anchor = next((a for a in anchors if "Metric" in a["label"] or "parsing" in a["label"]), None)

    if is_speculative_case(report):
        model_pair = _anchor_with_label(anchors, "target and drafter")
        knobs = _anchor_with_label(anchors, "generation knobs")
        spec_call = _anchor_with_label(anchors, "speculative call")
        baseline = _anchor_with_label(anchors, "autoregressive baseline")
        throughput = _anchor_with_label(anchors, "throughput")
        algorithm = _anchor_with_label(anchors, "core algorithm")
        verifier = _anchor_with_label(anchors, "target verifies")
        command = _first_run_command(commands, "python infer.py")
        return [
            ("1. Lock the reproduction claim", "Measure speculative decoding against target autoregressive decoding on the same prompts, target model, tokenizer, cache setting, and sampling processor. The demo metric should be tokens/sec plus acceptance rate, not just subjective output quality."),
            ("2. Choose the target/drafter pair", f"Start at {_anchor_ref(model_pair, '`infer.py`')}. The drafter must be much cheaper than the target, but close enough that drafts are accepted often."),
            ("3. Freeze gamma and decoding settings", f"Use {_anchor_ref(knobs, '`infer.py`')} to make gamma, max tokens, cache, top-k/top-p, and greedy-vs-sampling behavior explicit experiment parameters."),
            ("4. Run the side-by-side smoke test", f"Inspect the code, then adapt `{command}`. Feed a short fixed prompt set and record target AR, speculative, and ngram-assisted outputs separately."),
            ("5. Wrap the speculative call", f"Turn {_anchor_ref(spec_call, '`speculative_generate`')} into a batch function that returns output text, wall time, generated tokens, acceptance rate, and hardware metadata."),
            ("6. Keep the baseline honest", f"Use {_anchor_ref(baseline, '`autoregressive_generate`')} as the comparison path. The baseline must use the same target model and sampling processor as the speculative path."),
            ("7. Validate algorithm correctness", f"Treat {_anchor_ref(algorithm, '`sampling/speculative_decoding.py`')} and {_anchor_ref(verifier, 'the accept/reject block')} as correctness-critical code. Optimize around them only after a fixed-seed equality/distribution check passes."),
            ("8. Make the demo video concrete", f"Show one prompt, the acceptance rate, target AR tokens/sec, speculative tokens/sec, and the computed speedup from {_anchor_ref(throughput, 'the throughput print block')}."),
        ]

    if is_cot_case(report):
        run_cmd = _anchor_with_label(anchors, "gsm8k run")
        exemplars = _anchor_with_label(anchors, "few-shot")
        data = _anchor_with_label(anchors, "gsm8k data")
        prompt = _anchor_with_label(anchors, "prompt assembly")
        api = _anchor_with_label(anchors, "model/api")
        scoring = _anchor_with_label(anchors, "answer parsing")
        logging = _anchor_with_label(anchors, "result logging")
        command = _first_run_command(commands, "python gsm8k/run_gsm8k_claude_instant.py")
        return [
            ("1. Separate the two goals", "Exact paper-table reproduction means matching the original PaLM-era setup. Practical CoT reproduction is much easier: implement the few-shot reasoning prompt, run it on GSM8K-style questions with an accessible backend, and compare against a direct-answer baseline."),
            ("2. Start from the runnable GSM8K path", f"Use {_anchor_ref(run_cmd, '`readme.md`')} and adapt `{command}` into a small smoke test that writes structured results."),
            ("3. Preserve the actual CoT method", f"{_anchor_ref(exemplars, '`gsm8k/lib_prompt/prompt_original.txt`')} contains the worked examples. Keep these unchanged for benchmark mode, then create a product prompt variant separately."),
            ("4. Freeze the benchmark data", f"{_anchor_ref(data, '`gsm8k/run_gsm8k_claude_instant.py`')} selects GSM8K rows. Log the split and row ids so the demo can rerun the same examples."),
            ("5. Extract prompt construction", f"Refactor {_anchor_ref(prompt, 'the prompt assembly block')} into `build_cot_prompt(question, exemplars)`, and add `build_direct_prompt(question)` for the no-CoT baseline."),
            ("6. Make the model call swappable", f"{_anchor_ref(api, 'the provider call')} is the backend boundary. Record provider, model, temperature, max tokens, and retries for every run."),
            ("7. Score both reproduction and product value", f"Use {_anchor_ref(scoring, 'the exact-answer scorer')} for GSM8K accuracy, then add product metrics like latency, cost, refusal rate, and examples needing human review."),
            ("8. Save evidence for the demo", f"{_anchor_ref(logging, 'the output writer')} should become JSONL rows with question, prompt mode, raw output, parsed answer, gold answer, correctness, and runtime."),
        ]

    steps = [
        ("1. Pick the implementation route", f"{route}: {route_text}"),
        ("2. Reduce the paper to one product behavior", f"Target behavior: {report.benchmark}"),
        (
            "3. Start from the most relevant code anchor",
            (
                f"Inspect `{first_anchor['path']}:{first_anchor['range']}` first. "
                f"It is tagged as {first_anchor['label'].lower()} and should tell you where the implementation actually starts."
            )
            if first_anchor
            else _main_claim_text(report),
        ),
    ]
    if commands:
        steps.append(("4. Smoke-test the repo locally", f"Inspect the code first, then adapt this command: `{commands[0][1]}`"))
    else:
        steps.append(("4. Find or create the first runnable example", "No safe first command was inferred, so inspect README/examples or ask authors for a minimal command."))
    if prompt_anchor:
        steps.append(
            (
                "5. Extract the prompt builder",
                f"Turn `{prompt_anchor['path']}:{prompt_anchor['range']}` into a product prompt template, then keep the original prompt as a regression test.",
            )
        )
    else:
        steps.append(("5. Extract the core method", "Find the prompt/model/data boundary and turn it into a pure function that your app can call."))
    if model_anchor:
        steps.append(
            (
                "6. Swap the model backend deliberately",
                f"`{model_anchor['path']}:{model_anchor['range']}` is the provider call. Replace hard-coded models/keys with app configuration.",
            )
        )
    else:
        steps.append(("6. Swap the model backend deliberately", "Make model provider, decoding settings, timeout, and retry policy explicit configuration."))
    if metric_anchor:
        steps.append(
            (
                "7. Replace benchmark scoring with product scoring",
                f"`{metric_anchor['path']}:{metric_anchor['range']}` defines success. Replace it with your app's acceptance criteria.",
            )
        )
    else:
        steps.append(("7. Replace benchmark scoring with product scoring", "Create a tiny eval set that matches user behavior rather than paper benchmark rows."))
    steps.append(("8. Decide build/buy/skip", "Ship only if the anchored implementation beats a simple baseline on quality, cost, latency, and maintainability."))
    return steps


def implementation_questions(report: AuditReport) -> list[str]:
    questions = []
    categories = {m.category for m in report.overall_missing if m.severity in {"high", "medium"}}
    if "license" in categories or "code_availability" in categories:
        questions.append("Can I legally and practically use this implementation in my product?")
    if "checkpoint" in categories:
        questions.append("Are the required weights/checkpoints public, stable, and affordable to host or call?")
    if "hardware" in categories or "compute_budget" in categories:
        questions.append("What hardware or API budget do I need for acceptable latency and cost?")
    if "evaluation_script" in categories or "data_split" in categories:
        questions.append("How will I know my implementation is behaving correctly for my target users?")
    if "hyperparameters" in categories or "training_recipe" in categories:
        questions.append("Which settings are essential, and which can be simplified for an MVP?")
    questions.append("What is the smallest demo that proves this paper helps my specific use case?")
    return questions[:6]


def render_implementation_center(
    report: AuditReport,
    *,
    repo_input: str | None,
    repo_relation: str | None,
    author_email: str | None,
) -> None:
    st.subheader("Implementation Center")
    route, route_text = implementation_route(report, repo_relation)
    st.markdown(
        f"""
        <div class="copy-block">
          <h3>{escape(route)}</h3>
          <p>{escape(route_text)}</p>
          <p>
            This center is for builders. It does not ask whether the paper's exact
            table can be reproduced; it asks whether an indie developer can turn the
            idea into a useful prototype and what must be verified before shipping.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Build readiness")
    st.dataframe(implementation_readiness(report, repo_relation), width="stretch", hide_index=True)

    render_code_anchors(report, repo_input=repo_input)

    st.markdown("### Prototype plan")
    for label, detail in implementation_steps(report, repo_relation):
        st.markdown(f"**{label}**")
        st.markdown(detail)

    render_expected_commands(report)

    st.markdown("### Product questions before you build")
    questions = implementation_questions(report)
    for question in questions:
        st.markdown(f"- {question}")

    subject = f"Implementation question about {report.paper_title or report.paper_id or 'your paper'}"
    body = (
        f"Hi,\n\n"
        f"I'm an independent developer exploring whether I can implement the idea from "
        f"{report.paper_title or report.paper_id or 'your paper'} for this use case:\n\n"
        f"{report.benchmark}\n\n"
        f"My current implementation route is: {route}.\n\n"
        f"The questions I need to resolve are:\n"
        + "\n".join(f"- {q}" for q in questions[:4])
        + "\n\nThanks,"
    )
    mailto = f"mailto:{quote(author_email or '')}?subject={quote(subject)}&body={quote(body)}"
    links = [_anchor("Ask about implementation", mailto, primary=True)]
    if repo_input:
        repo_href = _repo_link(repo_input)
        if repo_href:
            links.append(_anchor("Inspect selected repo", repo_href))
    st.markdown(f'<div class="link-grid">{"".join(links)}</div>', unsafe_allow_html=True)


def render_action_links(
    report: AuditReport,
    *,
    paper_input: str | None,
    repo_input: str | None,
    author_email: str | None,
) -> None:
    links: list[str] = []
    paper_href = _paper_link(report, paper_input)
    repo_href = _repo_link(repo_input)
    if paper_href:
        links.append(_anchor("Open paper", paper_href))
    if repo_href:
        links.append(_anchor("Open repo", repo_href))

    subject, body = _email_draft(report)
    mailto = f"mailto:{quote(author_email or '')}?subject={quote(subject)}&body={quote(body)}"
    links.append(_anchor("Email authors", mailto, primary=True))
    links.append(_anchor("Project repo", "https://github.com/rli007/cs153", dark=True))

    st.markdown(f'<div class="link-grid">{"".join(links)}</div>', unsafe_allow_html=True)
    st.download_button(
        "Download audit JSON",
        data=report.model_dump_json(indent=2),
        file_name="repro-audit.json",
        mime="application/json",
        width="content",
    )


def render_email_panel(report: AuditReport, author_email: str | None) -> None:
    subject, body = _email_draft(report)
    mailto = f"mailto:{quote(author_email or '')}?subject={quote(subject)}&body={quote(body)}"
    st.subheader("Author follow-up")
    st.markdown(
        '<div class="link-grid">'
        + _anchor("Open email draft", mailto, primary=True)
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="email-preview">{escape(body)}</div>', unsafe_allow_html=True)


def render_repo(report: AuditReport) -> None:
    rs = report.repo_summary
    st.subheader("Repository summary")
    st.markdown(
        """
        <div class="copy-block">
          <p>
            This section is the system's first-pass map of the implementation.
            Entry points and evaluation scripts are inferred from file names,
            dependency files, repository structure, and short code excerpts.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    cols[0].metric("Important files", len(rs.important_files))
    cols[1].metric("Entry points", len(rs.likely_entry_points))
    cols[2].metric("Eval scripts", len(rs.likely_eval_scripts))
    if rs.likely_entry_points:
        st.markdown("**Likely entry points**")
        for f in rs.likely_entry_points:
            st.markdown(f'<div class="code-link">{f}</div>', unsafe_allow_html=True)
    if rs.likely_eval_scripts:
        st.markdown("**Likely eval scripts**")
        for f in rs.likely_eval_scripts:
            st.markdown(f'<div class="code-link">{f}</div>', unsafe_allow_html=True)
    if rs.notes:
        st.markdown("**Notes**")
        for n in rs.notes:
            st.markdown(f"- {n}")


def render_missing(report: AuditReport) -> None:
    if not report.overall_missing:
        st.info("No paper-level missing details flagged.")
        return
    st.subheader("Overall missing details")
    st.markdown(
        """
        <div class="copy-block">
          <p>
            Missing details are not accusations; they are implementation notes.
            Some are normal sourcing tasks for a competent builder, like choosing
            model weights, hardware, APIs, or dependency versions. Treat a gap as a
            true blocker only when it is private, unnamed, undisclosed, or defines
            the metric itself.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    rows = []
    for m in report.overall_missing:
        rows.append({
            "Severity": m.severity,
            "Type": "true blocker" if is_true_blocker_gap(m) else "sourcing/setup",
            "Category": m.category,
            "Description": m.description,
        })
    rows.sort(key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r["Severity"], 3))
    st.dataframe(rows, width="stretch", hide_index=True)


def render_claims(report: AuditReport, *, repo_input: str | None) -> None:
    st.subheader(f"Claims audit ({len(report.claims)})")
    st.markdown(
        """
        <div class="copy-block">
          <p>
            Each claim is a measurable result extracted from the paper. The audit
            links it to likely implementation files, then separates public sourcing
            tasks from true blockers. A dataset or model not being inside the selected
            repo is not treated as failure; the implementer is expected to search,
            configure, substitute, and document those choices.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for i, ca in enumerate(report.claims, start=1):
        c = ca.claim
        title = f"Claim {i}: {c.statement[:90]}{'...' if len(c.statement) > 90 else ''}"
        if c.is_main_claim:
            title = "Main claim - " + title
        with st.expander(title, expanded=(i == 1)):
            cols = st.columns([2, 1])
            with cols[0]:
                st.markdown(f"> {c.statement}")
                if c.metric:
                    bits = [f"**Metric:** {c.metric.name}"]
                    if c.metric.baseline_value is not None:
                        bits.append(f"baseline {c.metric.baseline_value}")
                    if c.metric.proposed_value is not None:
                        bits.append(f"proposed {c.metric.proposed_value}")
                    if c.metric.delta is not None:
                        bits.append(f"delta {c.metric.delta}")
                    st.markdown(" · ".join(bits))
                if c.dataset:
                    st.markdown(f"**Dataset:** {c.dataset.name} (split: {c.dataset.split or '?'})")
                if c.evidence:
                    st.markdown("**Evidence**")
                    for ev in c.evidence:
                        loc = f" _({ev.location})_" if ev.location else ""
                        st.markdown(f"> {ev.quote}{loc}")
            with cols[1]:
                practical_feasibility = practical_claim_feasibility(ca)
                st.markdown(
                    f"**Implementation feasibility** {feasibility_badge(practical_feasibility)}",
                    unsafe_allow_html=True,
                )
                if practical_feasibility != ca.feasibility:
                    st.caption(f"Exact paper-number feasibility from the raw audit: {ca.feasibility}.")
                if ca.blockers:
                    st.markdown("**Open work**")
                    for b in ca.blockers:
                        render_open_work_item(b)
            credible_links = [
                link
                for link in ca.code_links
                if (
                    link.confidence >= 0.5
                    and _repo_file_exists(report, link.path)
                    and _file_line_count(report, link.path) > 5
                    and "not explicitly found" not in link.rationale.lower()
                    and "if svamp were" not in link.rationale.lower()
                    and "would likely reside" not in link.rationale.lower()
                )
            ]
            if credible_links:
                st.markdown("**Candidate code links**")
                for link in credible_links:
                    href = _github_blob_link(repo_input, link.path)
                    path_label = (
                        f'<a href="{escape(href)}" target="_blank" rel="noopener noreferrer">{escape(link.path)}</a>'
                        if href
                        else escape(link.path)
                    )
                    st.markdown(
                        f'<div class="code-link">'
                        f'<b>{path_label}</b> - {escape(link.role)} '
                        f'<span class="small-muted">conf {link.confidence:.2f}</span><br>'
                        f'<span class="small-muted">{escape(link.rationale)}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            elif ca.code_links:
                st.markdown("**Candidate code links**")
                st.caption(
                    "No direct, usable repo link survived the availability-aware filter. "
                    "This usually means the artifact should be sourced externally or the repo only covers a neighboring benchmark."
                )
            if ca.missing:
                st.markdown("**Missing for this claim**")
                for m in ca.missing:
                    render_open_work_item(m.description, severity=m.severity, category=m.category)


def render_report(
    report: AuditReport,
    elapsed: float,
    *,
    paper_input: str | None,
    repo_input: str | None,
    author_email: str | None,
    repo_source: str | None = None,
    repo_relation: str | None = None,
    discovery_candidates: list[dict] | None = None,
) -> None:
    title = report.paper_title or report.paper_id or "Audit"
    st.markdown(
        f"""
        <div class="report-head">
          <div class="brand-mark"><span>RA</span><span>Audit complete</span></div>
          <h2>{escape(title)}</h2>
          <p>{escape(report.benchmark)}</p>
          <p><b>Implementation:</b> {escape(repo_relation or "unknown relation")}</p>
          <div class="signal-row">
            <div class="signal"><b>{len(report.claims)}</b><span>claims</span></div>
            <div class="signal"><b>{true_blocker_count(report)}</b><span>true blockers</span></div>
            <div class="signal"><b>{setup_task_count(report)}</b><span>setup tasks</span></div>
            <div class="signal"><b>{sum(len(c.code_links) for c in report.claims)}</b><span>code links</span></div>
          </div>
          <p><b>Feasibility</b> {feasibility_badge(report.overall_feasibility)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_action_links(
        report,
        paper_input=paper_input,
        repo_input=repo_input,
        author_email=author_email,
    )

    tab_overview, tab_implement, tab_claims, tab_missing, tab_repo, tab_ask, tab_email, tab_raw = st.tabs(
        ["Overview", "Implement", "Claims", "Missing details", "Repository", "Ask", "Email", "Raw JSON"]
    )

    with tab_overview:
        render_paper_context(report, paper_input)
        st.markdown(
            """
            <div class="copy-block">
              <h3>Read this like a pre-flight review</h3>
              <p>
                A high verdict means the paper and repo expose enough implementation detail
                for a reasonable reproduction attempt. Medium means the path exists but some
                important assumptions remain. Low means the exact paper-number path is weak,
                not that an implementer cannot build the method. Treat public model/dataset/API
                sourcing as normal work; reserve author clarification for private, unnamed, or
                metric-defining details.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Claims", len(report.claims))
        c2.metric("True blockers", true_blocker_count(report))
        total_links = sum(len(c.code_links) for c in report.claims)
        c3.metric("Code links", total_links)
        c4.metric("Sourcing tasks", setup_task_count(report))
        if report.risks:
            st.markdown("### Risks")
            for r in report.risks:
                st.markdown(f"- {r}")
        if report.next_steps:
            st.markdown("### Next steps")
            for i, step in enumerate(report.next_steps, start=1):
                st.markdown(f"{i}. {step}")

    with tab_implement:
        render_implementation_center(
            report,
            repo_input=repo_input,
            repo_relation=repo_relation,
            author_email=author_email,
        )
    with tab_claims:
        render_claims(report, repo_input=repo_input)
    with tab_missing:
        render_missing(report)
    with tab_repo:
        render_repo_provenance(
            repo_input=repo_input,
            repo_source=repo_source,
            repo_relation=repo_relation,
            discovery_candidates=discovery_candidates,
        )
        render_author_panel(report, author_email)
        render_repo_health(report)
        render_expected_commands(report)
        render_repo(report)
    with tab_ask:
        render_ask_panel(report, author_email)
    with tab_email:
        render_email_panel(report, author_email)
    with tab_raw:
        st.code(report.model_dump_json(indent=2), language="json")


# ---------- Run logic ----------
def run_audit(inputs: CopilotInput, status_box) -> tuple[AuditReport, float]:
    start = time.time()

    status_box.update(label="Ingesting paper + repo...", state="running")
    report = build_audit(inputs)
    elapsed = time.time() - start
    status_box.update(label=f"Audit complete in {elapsed:.1f}s", state="complete")
    return report, elapsed


# ---------- Main panel ----------
if run_button:
    if not paper or not benchmark:
        st.error("Please fill in the paper link/arXiv id and what you are trying to reproduce.")
    else:
        with st.status("Running audit...", expanded=True) as status_box:
            try:
                status_box.update(label="Searching for an implementation repo...", state="running")
                if repo_override.strip():
                    resolved_repo = repo_override.strip()
                    repo_source = "manual override"
                    repo_relation = "manual repository; relation not verified"
                    discovery_candidates: list[dict] = []
                else:
                    resolved_repo, repo_source, discovery_candidates, repo_relation = discover_repo_for_paper(paper)
                if resolved_repo:
                    st.info(f"Using repository from {repo_source}: {resolved_repo} ({repo_relation})")
                else:
                    st.warning(
                        "No high-confidence implementation repository was found. "
                        "The app will run a paper-only triage, then suggest what code, docs, or public implementations to source next."
                    )
                inputs = CopilotInput(
                    paper=paper,
                    repo=resolved_repo,
                    benchmark=benchmark,
                    model_card=model_card or None,
                    reviews=reviews or None,
                    use_retrieval=use_retrieval,
                )
                report, elapsed = run_audit(inputs, status_box)
            except Exception as exc:
                st.error(f"Audit failed: {exc}")
            else:
                st.session_state["last_report"] = report
                st.session_state["last_elapsed"] = elapsed
                st.session_state["last_inputs"] = {
                    "paper": paper,
                    "repo": resolved_repo,
                    "author_email": author_email,
                    "repo_source": repo_source,
                    "repo_relation": repo_relation,
                    "discovery_candidates": discovery_candidates,
                }

if "last_report" in st.session_state:
    last_inputs = st.session_state.get("last_inputs", {})
    render_report(
        st.session_state["last_report"],
        st.session_state["last_elapsed"],
        paper_input=last_inputs.get("paper"),
        repo_input=last_inputs.get("repo"),
        author_email=last_inputs.get("author_email"),
        repo_source=last_inputs.get("repo_source"),
        repo_relation=last_inputs.get("repo_relation"),
        discovery_candidates=last_inputs.get("discovery_candidates"),
    )
else:
    st.markdown(
        """
        <div class="report-head">
          <div class="brand-mark"><span>01</span><span>Bench snapshot</span></div>
          <h2>Pre-flight checks for serious reproduction work.</h2>
          <p>
            Choose a paper and repository from the run panel. The dashboard turns
            the audit into links, blockers, and author follow-ups instead of a loose summary.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    bench_summary_path = Path("outputs/bench/real_papers_v3/bench_summary.json")
    if bench_summary_path.exists():
        bench = json.loads(bench_summary_path.read_text())
        agg = bench["aggregate"]
        st.markdown("### Real-paper benchmark")
        cols = st.columns(5)
        cols[0].metric("Papers", len(bench["papers"]))
        cols[1].metric("Claim coverage", f"{agg['claim_coverage']:.2f}")
        cols[2].metric("Gap F1", f"{agg['gap_f1']:.2f}")
        cols[3].metric("Link accuracy", f"{agg['link_accuracy']:.2f}")
        cols[4].metric("Overall", f"{agg['overall']:.2f}")
        st.dataframe(
            [
                {
                    "paper": p["paper_id"],
                    "claim_cov": p["rubric"]["claim_coverage"],
                    "gap_f1": p["rubric"]["gap_f1"],
                    "link_acc": p["rubric"]["link_accuracy"],
                    "feas_pass": p["rubric"]["feasibility_pass"],
                    "agg": (
                        p["rubric"]["claim_coverage"]
                        + p["rubric"]["gap_f1"]
                        + p["rubric"]["link_accuracy"]
                        + (1.0 if p["rubric"]["feasibility_pass"] else 0.0)
                    )
                    / 4,
                }
                for p in bench["papers"]
            ],
            width="stretch",
            hide_index=True,
        )

st.divider()
st.markdown(
    '<div class="link-grid">'
    + _anchor("GitHub", "https://github.com/rli007/cs153", dark=True)
    + _anchor("PaperBench context", "https://paperbench.ai/")
    + "</div>",
    unsafe_allow_html=True,
)
