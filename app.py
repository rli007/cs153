"""Streamlit demo UI for the Research Workflow Copilot.

Run with: ``streamlit run app.py``

Designed for live video demo: paste an arXiv id and a GitHub URL, click Run,
and watch the audit produce structured claims, missing details, code links,
and a feasibility verdict. Pre-loaded examples surface known-good runs from
the on-disk LLM cache (zero cost, instant playback).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import streamlit as st

from research_copilot.config import MODEL_ROUTES
from research_copilot.workflow import CopilotInput, build_audit
from research_copilot.schemas import AuditReport


st.set_page_config(
    page_title="Reproducibility Audit Copilot",
    page_icon="🔬",
    layout="wide",
)


# ---------- Styling ----------
st.markdown(
    """
    <style>
      .feasibility-high {background: #DCFCE7; color: #166534; padding: 6px 14px;
                         border-radius: 999px; font-weight: 600; display: inline-block;}
      .feasibility-medium {background: #FEF3C7; color: #92400E; padding: 6px 14px;
                            border-radius: 999px; font-weight: 600; display: inline-block;}
      .feasibility-low {background: #FEE2E2; color: #991B1B; padding: 6px 14px;
                         border-radius: 999px; font-weight: 600; display: inline-block;}
      .severity-high {color: #991B1B; font-weight: 600;}
      .severity-medium {color: #92400E; font-weight: 600;}
      .severity-low {color: #166534; font-weight: 600;}
      .small-muted {color: #6B7280; font-size: 0.85em;}
      .code-link {background: #F3F4F6; padding: 8px 12px; border-radius: 6px;
                   margin-bottom: 6px; font-family: ui-monospace, monospace; font-size: 0.85em;}
      blockquote {border-left: 3px solid #94A3B8; padding-left: 12px; color: #475569;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Header ----------
st.title("🔬 Reproducibility Audit Copilot")
st.markdown(
    "**Predict whether a paper is reproducible — without running anything.** "
    "Frontier agents (PaperBench) replicate ML papers at ~21–26% after 12+ hours of compute. "
    "This system runs an evidence-grounded audit in **4 LLM calls (~$0.05) per paper**, with claim→code "
    "traceability backed by local embedding retrieval."
)


# ---------- Sidebar ----------
with st.sidebar:
    st.header("Inputs")

    examples = {
        "(custom)": None,
        "Sample (toy)": {
            "paper": "examples/sample_paper.txt",
            "repo": ".",
            "benchmark": "reproduce the macro F1 improvement on the held-out validation split",
            "model_card": "examples/sample_model_card.txt",
        },
        "LoRA (2106.09685)": {
            "paper": "2106.09685",
            "repo": "https://github.com/microsoft/LoRA",
            "benchmark": "Reproduce LoRA fine-tuning of GPT-2 medium on E2E NLG (Table 2 BLEU/ROUGE).",
            "model_card": None,
        },
        "FlashAttention (2205.14135)": {
            "paper": "2205.14135",
            "repo": "https://github.com/Dao-AILab/flash-attention",
            "benchmark": "Reproduce FlashAttention end-to-end speedup on GPT-2 training (Table 1).",
            "model_card": None,
        },
        "DPO (2305.18290)": {
            "paper": "2305.18290",
            "repo": "https://github.com/eric-mitchell/direct-preference-optimization",
            "benchmark": "Reproduce DPO on IMDB sentiment vs PPO (Section 6 win-rate).",
            "model_card": None,
        },
        "Mamba (2312.00752)": {
            "paper": "2312.00752",
            "repo": "https://github.com/state-spaces/mamba",
            "benchmark": "Reproduce Mamba on Pile language modeling perplexity (Table 4).",
            "model_card": None,
        },
    }
    pick = st.selectbox("Preset", list(examples.keys()), index=1)
    preset = examples[pick] or {}

    paper = st.text_input(
        "Paper",
        value=preset.get("paper", ""),
        help="arXiv id (2501.12345), URL, local PDF/TXT path.",
    )
    repo = st.text_input(
        "Repo",
        value=preset.get("repo", ""),
        help="Local path or GitHub URL (will be shallow-cloned).",
    )
    benchmark = st.text_area(
        "Benchmark target",
        value=preset.get("benchmark", ""),
        help="What you want to reproduce, in plain English.",
        height=80,
    )

    with st.expander("Optional"):
        model_card = st.text_input(
            "Model card",
            value=preset.get("model_card", "") or "",
            help="File path or HuggingFace URL.",
        )
        reviews = st.text_input(
            "OpenReview URL",
            value=preset.get("reviews", "") or "",
            help="OpenReview forum URL or note id.",
        )
        use_retrieval = st.checkbox("Use local embedding retrieval", value=True)

    run_button = st.button("🚀 Run audit", type="primary", use_container_width=True)

    st.divider()
    st.subheader("Active model routes")
    for role, models in MODEL_ROUTES.items():
        st.markdown(f"**{role}** → `{models[0]}`")
    st.caption("Falls through on 429/404 to the next model.")


# ---------- Render helpers ----------
def feasibility_badge(value: str) -> str:
    cls = f"feasibility-{value}"
    return f'<span class="{cls}">{value.upper()}</span>'


def severity_class(value: str) -> str:
    return f"severity-{value}"


def render_repo(report: AuditReport) -> None:
    rs = report.repo_summary
    st.subheader("Repository summary")
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
    rows = []
    for m in report.overall_missing:
        rows.append({"Severity": m.severity, "Category": m.category, "Description": m.description})
    rows.sort(key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r["Severity"], 3))
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_claims(report: AuditReport) -> None:
    st.subheader(f"Claims audit ({len(report.claims)})")
    for i, ca in enumerate(report.claims, start=1):
        c = ca.claim
        title = f"Claim {i}: {c.statement[:90]}{'…' if len(c.statement) > 90 else ''}"
        if c.is_main_claim:
            title = "🎯 " + title
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
                        bits.append(f"Δ {c.metric.delta}")
                    st.markdown(" · ".join(bits))
                if c.dataset:
                    st.markdown(f"**Dataset:** {c.dataset.name} (split: {c.dataset.split or '?'})")
                if c.evidence:
                    st.markdown("**Evidence**")
                    for ev in c.evidence:
                        loc = f" _({ev.location})_" if ev.location else ""
                        st.markdown(f"> {ev.quote}{loc}")
            with cols[1]:
                st.markdown(f"**Feasibility** {feasibility_badge(ca.feasibility)}", unsafe_allow_html=True)
                if ca.blockers:
                    st.markdown("**Blockers**")
                    for b in ca.blockers:
                        st.markdown(f"- {b}")
            if ca.code_links:
                st.markdown("**Candidate code links**")
                for link in ca.code_links:
                    st.markdown(
                        f'<div class="code-link">'
                        f'<b>{link.path}</b> — {link.role} '
                        f'<span class="small-muted">conf {link.confidence:.2f}</span><br>'
                        f'<span class="small-muted">{link.rationale}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            if ca.missing:
                st.markdown("**Missing for this claim**")
                for m in ca.missing:
                    st.markdown(
                        f'- <span class="{severity_class(m.severity)}">[{m.severity}]</span> '
                        f'<b>{m.category}</b> — {m.description}',
                        unsafe_allow_html=True,
                    )


def render_report(report: AuditReport, elapsed: float) -> None:
    cols = st.columns([2, 1, 1])
    with cols[0]:
        title = report.paper_title or report.paper_id or "Audit"
        st.markdown(f"## {title}")
        st.caption(report.benchmark)
    with cols[1]:
        st.metric("Wall time", f"{elapsed:.1f}s")
    with cols[2]:
        st.markdown(
            f"**Feasibility** {feasibility_badge(report.overall_feasibility)}",
            unsafe_allow_html=True,
        )
    st.divider()

    tab_overview, tab_claims, tab_missing, tab_repo, tab_raw = st.tabs(
        ["Overview", "Claims", "Missing details", "Repository", "Raw JSON"]
    )

    with tab_overview:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Claims", len(report.claims))
        high = sum(1 for m in report.overall_missing if m.severity == "high")
        c2.metric("High-severity gaps", high)
        total_links = sum(len(c.code_links) for c in report.claims)
        c3.metric("Code links", total_links)
        c4.metric(
            "Avg link conf",
            f"{(sum(l.confidence for c in report.claims for l in c.code_links) / max(1, total_links)):.2f}"
            if total_links
            else "—",
        )
        if report.risks:
            st.markdown("### Risks")
            for r in report.risks:
                st.markdown(f"- {r}")
        if report.next_steps:
            st.markdown("### Next steps")
            for i, step in enumerate(report.next_steps, start=1):
                st.markdown(f"{i}. {step}")

    with tab_claims:
        render_claims(report)
    with tab_missing:
        render_missing(report)
    with tab_repo:
        render_repo(report)
    with tab_raw:
        st.code(report.model_dump_json(indent=2), language="json")


# ---------- Run logic ----------
def run_audit(inputs: CopilotInput, status_box) -> tuple[AuditReport, float]:
    start = time.time()

    status_box.update(label="Ingesting paper + repo…", state="running")
    report = build_audit(inputs)
    elapsed = time.time() - start
    status_box.update(label=f"Audit complete in {elapsed:.1f}s", state="complete")
    return report, elapsed


# ---------- Main panel ----------
if run_button:
    if not paper or not repo or not benchmark:
        st.error("Please fill in paper, repo, and benchmark.")
    else:
        with st.status("Running audit…", expanded=True) as status_box:
            try:
                inputs = CopilotInput(
                    paper=paper,
                    repo=repo,
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

if "last_report" in st.session_state:
    render_report(st.session_state["last_report"], st.session_state["last_elapsed"])
else:
    st.info(
        "Pick a preset on the left and click **Run audit**. "
        "First run takes ~30–60s and ~$0.05; cached re-runs are instant."
    )

    bench_summary_path = Path("outputs/bench/real_papers_v2/bench_summary.json")
    if bench_summary_path.exists():
        st.divider()
        st.markdown("### Live bench results")
        bench = json.loads(bench_summary_path.read_text())
        agg = bench["aggregate"]
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
            use_container_width=True,
            hide_index=True,
        )

st.divider()
st.caption(
    "Built for CS 153. Models via OpenRouter. Embeddings via sentence-transformers (local). "
    "Code: github.com/rli007/cs153"
)
