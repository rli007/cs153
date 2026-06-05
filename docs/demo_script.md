# Demo video script — Reproducibility Audit Copilot

Target length: **3 minutes**, recorded as a screen capture with voiceover.
Pre-warm the LLM cache for every preset so re-runs are instant.

---

## 0:00–0:25 — Hook & problem (25 s)

> "Last year OpenAI ran PaperBench, where they asked Claude- and o1-class
> agents to reproduce 20 ML papers from scratch. After **12 hours of
> compute and over a thousand dollars per attempt**, the agents
> succeeded **about 21% of the time**. Humans hit 41% — over 48 hours.
> So the obvious question is: can we *predict* whether a paper is
> reproducible *before* anyone burns that compute?"

[Cut to README hero shot of the Streamlit landing.]

---

## 0:25–1:00 — The pitch (35 s)

> "This is a Reproducibility Audit Copilot. You give it an arXiv paper
> and a GitHub repo. In **four LLM calls and about five cents**, it
> emits a structured audit: every empirical claim with metric values
> and verbatim evidence, every missing reproducibility detail
> categorized and ranked, and per-claim links into the repo backed by
> local embedding retrieval — *no code execution*."

[Show the Streamlit UI sidebar with the LoRA preset selected.]

---

## 1:00–2:00 — Live audit on LoRA (60 s)

[Click **Run audit**. Show the live status box.]

> "Behind that one button: pull the arXiv PDF, shallow-clone the repo,
> chunk and embed every code file locally, extract claims with one LLM
> call, detect missing details with another, tag entry points and eval
> scripts with a third, and finally a per-claim audit step that gets
> the retrieved code chunks for *that specific claim* and emits links,
> blockers, and a feasibility verdict."

[Once the result lands, walk through tabs:]
- **Overview** — feasibility badge, claim/gap/link counters, risks,
  next steps.
- **Claims** — expand the LoRA main claim. Point at: metric values,
  evidence quote, candidate code links with confidence, missing
  details for *this* claim.
- **Missing details** — sortable severity table.
- **Repository** — entry points / eval scripts / dependency files.
- **Raw JSON** — show the strict, machine-readable schema.

---

## 2:00–2:35 — Bench results (35 s)

[Scroll to "Live bench results" panel on the landing page, or open
`outputs/bench/real_papers_v1/bench_summary.md`.]

> "Five real papers — LoRA, FlashAttention, DPO, Mamba, QLoRA —
> hand-curated ground truth, scored by a four-axis rubric. Whole bench
> runs in **under four minutes** and **30 cents**. Claim coverage 0.80,
> link accuracy 1.0. The model is also strict about reproducibility,
> which lines up with what PaperBench actually measures."

---

## 2:35–3:00 — Wrap (25 s)

> "It's a useful primitive on its own — get a one-page audit before
> committing to a reproduction — and a clean front end for any heavier
> execution agent. Code, evals, README, and disclosure are in the repo."

[Show the README "AI usage disclosure" section briefly, then end card.]

---

## Stage prep checklist

- `streamlit run app.py` running and warm in another window.
- All five real-paper presets pre-cached (run them once before recording).
- Browser at 1400×900, light theme, dev tools off.
- `outputs/bench/real_papers_v1/bench_summary.md` open in a side tab.
- Screen recorder set to 1080p, 30fps.
