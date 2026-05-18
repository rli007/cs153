# Project Milestone

## Q1 Project Title

Research Workflow Copilot: Converting Research Artifacts into Reproducible Experiments

## Q2 Project Track

Automation / Agent Systems

This project also has a strong applied-AI and research tooling component, but the best fit is Automation / Agent Systems because the central goal is to coordinate document understanding, repository inspection, experiment planning, and eventually experiment execution.

## Q3 Progress

I have started building the base scaffold for an AI research copilot that turns papers and related artifacts into reproducible experiment workflows. The current version includes a Python CLI that accepts a paper text file, repository path, benchmark/task description, and optional model card, then produces a first-pass reproduction plan with extracted candidate claims, missing implementation details, repository observations, and experiment steps.

Most of the current progress is scaffolding, but it establishes the main system boundaries: paper understanding, repo inspection, structured planning, and report generation. I also added sample inputs so the workflow can be run end to end without external dependencies.

## Q4 Future Implementation

Next, I plan to replace the heuristic claim extraction with an LLM-backed structured extraction pipeline that identifies empirical claims, metrics, datasets, baselines, and assumptions from papers. I also plan to add PDF parsing, retrieval over README files and technical docs, deeper codebase understanding, and automatic generation of runnable experiment configs or scripts.

After that, I want the system to partially execute experiments in a controlled way: run smoke tests, launch small benchmark runs, collect logs and metrics, and summarize what reproduced versus what failed. The final version should produce a reproducibility report that clearly explains the evidence, missing details, and next steps.

## Q5 Github Link

https://github.com/rli007/cs153

## Q6 Compute

For the current scaffold, no special compute is needed because the prototype uses lightweight Python scripts and sample text files. Later stages may need GPU access or cloud compute for reproducing model training/inference experiments, especially if the selected papers involve large language models, vision models, or benchmark-scale evaluation.
