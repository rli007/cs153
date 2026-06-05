# Reproducibility Audit

**Paper id:** `2305.14314`
**Benchmark target:** Reproduce QLoRA fine-tuning of LLaMA-7B on Alpaca and recover the MMLU score from Table 6.
**Overall feasibility:** `medium`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/artidoro__qlora`
- Important files: README.md, requirements.txt
- Likely entry points: qlora.py
- Likely eval scripts: eval/eval_gpt_review.py, eval/qa_baseline_gpt.py
- Likely config files: none detected
- Dependency files: eval/requirements.txt, requirements.txt
- Has tests: False
- Notes:
  - uses Hydra configs under configs/
  - no requirements file detected

## Overall Missing Details

- **[medium] random_seed** — The paper mentions using random seeds for Elo rating calculations (10,000 times) and for individual runs (Figure 2), but the specific seeds used are not provided.
- **[low] hardware** — While the paper mentions using a single 48GB GPU for finetuning a 65B model and a single consumer GPU for a 33B model, the specific GPU model(s) used are not detailed. This information is important for understanding the practical limitations and potential for reproduction.
- **[high] data_split** — The paper mentions using various datasets for training and evaluation (e.g., OASST1, HH-RLHF, FLANv2, Alpaca, Vicuna benchmark, OA benchmark). However, the specific splits for training, validation, and testing for these datasets are not detailed, especially for the evaluation benchmarks.
- **[medium] hyperparameters** — While some hyperparameters are provided (e.g., LoRA r, alpha, dropout, Adam betas, learning rate schedule, batch size, sequence length, gradient checkpointing), specific values for all hyperparameters used in the experiments, especially for the evaluation phase and for all model sizes, are not fully detailed. For instance, the exact learning rate for each model size and dataset combination is provided in Table 9, but other hyperparameters like weight decay or optimizer specific parameters are not always explicitly stated for all experiments.
- **[high] checkpoint** — The paper mentions releasing all models and code, and provides adapters for various model sizes. However, it does not explicitly state if full model checkpoints (not just adapters) are released or how to obtain them, which would be crucial for reproducing the exact finetuned models.
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.
- **[medium] data_preprocessing** — The paper mentions using various datasets and preprocessing them (e.g., for Super-NaturalInstructions, OASST1, HH-RLHF). However, the exact preprocessing steps for each dataset, especially for the instruction tuning datasets and the evaluation benchmarks, are not fully detailed, which could lead to variations in performance.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.
- **[low] license** — The paper mentions releasing code and models, but the specific licenses under which they are released are not stated. This is important for understanding the terms of use and redistribution.
- **[low] compute_budget** — The paper mentions training time (e.g., 24 hours on a single GPU for a 65B model, less than 12 hours for a 33B model on a consumer GPU) and memory usage (e.g., 48GB GPU for 65B model). However, a precise breakdown of the total compute budget (e.g., FLOPs, GPU hours across all experiments) is not provided, which would be useful for understanding the overall cost and scalability.

## Claims Audit

### Claim 1 — _main claim_

> QLORA reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance.

**Method:** QLORA vs **Baseline:** ?
**Feasibility:** `medium`

**Evidence:**
> We present QLORA, an efficient finetuning approach that reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance.

**Code links:**
- `qlora.py` — training entry (confidence 0.52): This file contains the main training logic and arguments related to quantization and memory usage, such as `bnb_4bit_use_double_quant` and `per_device_train_batch_size`.
- `README.md` — explanation (confidence 0.47): The README introduces QLoRA and mentions its efficiency in finetuning quantized LLMs, aligning with the claim of reduced memory usage.

**Missing for this claim:**
- **[low] hardware** — While the paper mentions using a single 48GB GPU for finetuning a 65B model and a single consumer GPU for a 33B model, the specific GPU model(s) used are not detailed. This information is important for understanding the practical limitations and potential for reproduction.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.

**Blockers:**
- Specific GPU model used for 65B model training
- Full training recipe details (e.g., exact number of steps, gradient accumulation)

### Claim 2

> QLORA reduces the average memory requirements of finetuning a 65B parameter model from >780GB of GPU memory to <48GB without degrading the runtime or predictive performance compared to a 16-bit fully finetuned baseline.

**Method:** QLORA vs **Baseline:** 16-bit fully finetuned baseline
**Feasibility:** `medium`

**Evidence:**
> QLORA reduces the average memory requirements of finetuning a 65B parameter model from >780GB of GPU memory to <48GB without degrading the runtime or predictive performance compared to a 16-bit fully finetuned baseline.

**Code links:**
- `qlora.py` — training entry (confidence 0.46): This file contains the core QLoRA implementation, including parameters for 4-bit quantization (`bnb_4bit_use_double_quant`, `bnb_4bit_quant_type`) which directly relate to memory reduction.
- `README.md` — explanation (confidence 0.46): The README highlights QLoRA's efficiency in finetuning quantized LLMs, which is central to the claim about memory reduction.

**Missing for this claim:**
- **[low] hardware** — While the paper mentions using a single 48GB GPU for finetuning a 65B model and a single consumer GPU for a 33B model, the specific GPU model(s) used are not detailed. This information is important for understanding the practical limitations and potential for reproduction.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.

**Blockers:**
- Specific GPU model for 65B model training
- Full training recipe details for the 16-bit baseline
- Evaluation scripts for comparing predictive performance against a 16-bit baseline

### Claim 3

> Using QLORA, the Guanaco family of models, with the second best model reaching 97.8% of the performance level of ChatGPT on the Vicuna benchmark, while being trainable in less than 12 hours on a single consumer GPU.

**Metric:** performance relative to ChatGPT on Vicuna benchmark · proposed 97.8
**Dataset:** Vicuna benchmark
**Method:** QLORA (Guanaco) vs **Baseline:** ?
**Feasibility:** `medium`

**Evidence:**
> Using QLORA, we train the Guanaco family of models, with the second best model reaching 97.8% of the performance level of ChatGPT on the Vicuna [10] benchmark, while being trainable in less than 12 hours on a single consumer GPU;

**Code links:**
- `eval/EVAL_README.md` — explanation (confidence 0.44): This README describes the evaluation process using GPT-4 and mentions the Vicuna benchmark queries, which are directly relevant to the claim's evaluation metric and dataset.
- `eval/qa_baseline_gpt.py` — eval script (confidence 0.42): This script is used to generate answers with GPT-3.5/GPT-4, which is a component of the Vicuna benchmark evaluation as described in the paper and `EVAL_README.md`.
- `scripts/finetune_guanaco_65b.sh` — training entry (confidence 0.42): This script shows how to finetune a Guanaco 65B model, which is part of the Guanaco family mentioned in the claim.
- `scripts/finetune_guanaco_13b.sh` — training entry (confidence 0.42): This script shows how to finetune a Guanaco 13B model, which is part of the Guanaco family mentioned in the claim.
- `scripts/finetune_guanaco_7b.sh` — training entry (confidence 0.42): This script shows how to finetune a Guanaco 7B model, which is part of the Guanaco family mentioned in the claim.
- `qlora.py` — training entry (confidence 0.42): This is the main training script for QLoRA models, which would be used to train the Guanaco models.

**Missing for this claim:**
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.
- **[low] hardware** — While the paper mentions using a single 48GB GPU for finetuning a 65B model and a single consumer GPU for a 33B model, the specific GPU model(s) used are not detailed. This information is important for understanding the practical limitations and potential for reproduction.

**Blockers:**
- Full evaluation pipeline for Vicuna benchmark (beyond generation)
- Specific consumer GPU model and its configuration
- Exact training recipe for Guanaco models

### Claim 4

> Using a single professional GPU over 24 hours we achieve 99.3% [of ChatGPT performance] with our largest model, essentially closing the gap to ChatGPT on the Vicuna benchmark.

**Metric:** performance relative to ChatGPT on Vicuna benchmark · proposed 99.3
**Dataset:** Vicuna benchmark
**Method:** QLORA (largest model) vs **Baseline:** ChatGPT
**Feasibility:** `medium`

**Evidence:**
> using a single professional GPU over 24 hours we achieve 99.3% with our largest model, essentially closing the gap to ChatGPT on the Vicuna bench- mark.

**Code links:**
- `eval/qa_baseline_gpt.py` — eval script (confidence 0.42): This script is used to generate answers with GPT-3.5/GPT-4, which is a component of the Vicuna benchmark evaluation as described in the paper and `EVAL_README.md`.
- `eval/EVAL_README.md` — explanation (confidence 0.41): This README describes the evaluation process using GPT-4 and mentions the Vicuna benchmark queries, which are directly relevant to the claim's evaluation metric and dataset.
- `qlora.py` — training entry (confidence 0.41): This is the main training script for QLoRA models, which would be used to train the largest Guanaco model.
- `eval/eval_gpt_review.py` — eval script (confidence 0.37): This script is for evaluating model responses using GPT-4, which is crucial for the Vicuna benchmark and comparing performance to ChatGPT.

**Missing for this claim:**
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.
- **[low] hardware** — While the paper mentions using a single 48GB GPU for finetuning a 65B model and a single consumer GPU for a 33B model, the specific GPU model(s) used are not detailed. This information is important for understanding the practical limitations and potential for reproduction.

**Blockers:**
- Full evaluation pipeline for Vicuna benchmark (beyond generation)
- Specific professional GPU model and its configuration
- Exact training recipe for the largest Guanaco model

### Claim 5

> When deployed, our smallest Guanaco model (7B parameters) requires just 5GB of memory and outperforms a 26GB Alpaca model by more than 20 percentage points on the Vicuna benchmark.

**Metric:** performance on Vicuna benchmark · delta 20.0
**Dataset:** Vicuna benchmark
**Method:** Guanaco 7B vs **Baseline:** Alpaca 26GB model
**Feasibility:** `medium`

**Evidence:**
> Whendeployed,oursmallestGuanacomodel(7Bparameters)requiresjust5GBofmemoryandoutperformsa26GBAlpacamodelbymorethan20percentagepointson theVicunabenchmark(Table6).

**Code links:**
- `scripts/finetune_guanaco_7b.sh` — training entry (confidence 0.44): This script demonstrates how to finetune the Guanaco 7B model, which is the subject of this claim.
- `eval/EVAL_README.md` — explanation (confidence 0.43): This README describes the evaluation process using GPT-4 and mentions the Vicuna benchmark queries, which are directly relevant to the claim's evaluation metric and dataset.
- `eval/generations/vicuna/7b-guanaco-vicuna-generations-topp0.9-temp0.7.jsonl` — eval data (confidence 0.90): This file contains generated responses for the 7B Guanaco model on the Vicuna benchmark, directly supporting the claim's evaluation.
- `eval/generations/vicuna/13b-alpaca-vicuna-generations-topp0.9-temp0.7.jsonl` — eval data (confidence 0.90): This file contains generated responses for an Alpaca model on the Vicuna benchmark, which could be used as a baseline for comparison.

**Missing for this claim:**
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.
- **[high] checkpoint** — The paper mentions releasing all models and code, and provides adapters for various model sizes. However, it does not explicitly state if full model checkpoints (not just adapters) are released or how to obtain them, which would be crucial for reproducing the exact finetuned models.

**Blockers:**
- Full evaluation pipeline for Vicuna benchmark (beyond generation)
- Exact training recipe for Guanaco 7B and Alpaca 26GB models
- Access to the Alpaca 26GB model checkpoint for comparison

### Claim 6

> NF4 improves performances significantly over FP4 and Int4 and that double quantization reduces the memory footprint without degrading performance.

**Method:** NF4 + DQ vs **Baseline:** FP4, Int4
**Feasibility:** `medium`

**Evidence:**
> Wefigure3andTable2weseethatNF4improvesper- formancesignificantlyoverFP4andInt4andthat doublequantizationreducesthememoryfootprint withoutdegradingperformance.

**Code links:**
- `README.md` — explanation (confidence 0.49): The README explains the quantization parameters, including `bnb_4bit_use_double_quant` and `bnb_4bit_quant_type`, which are directly relevant to NF4, FP4, Int4, and double quantization.
- `qlora.py` — training entry (confidence 0.33): This file contains the implementation details for `bnb_4bit_use_double_quant` and `bnb_4bit_quant_type`, which control the quantization types (NF4, FP4, Int4) and double quantization.

**Missing for this claim:**
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.

**Blockers:**
- Specific configurations (hyperparameters, datasets) used for comparing NF4, FP4, and Int4
- Evaluation scripts to measure performance differences between quantization types

### Claim 7

> NF4 with double quantization fully recovers the 16-bit LoRA MMLU performance.

**Dataset:** MMLU
**Method:** NF4 + DQ vs **Baseline:** 16-bit LoRA
**Feasibility:** `medium`

**Evidence:**
> We see that NF4 with double quantization fully recovers the 16-bit LoRA MMLU performance.

**Code links:**
- `README.md` — explanation (confidence 0.53): The README explains the quantization parameters, including `bnb_4bit_use_double_quant` and `bnb_4bit_quant_type`, which are directly relevant to NF4 and double quantization.
- `qlora.py` — training entry (confidence 0.34): This file contains the implementation details for `bnb_4bit_use_double_quant` and `bnb_4bit_quant_type`, which control the quantization types (NF4) and double quantization.
- `data/mmlu/five_shot_mmlu_test.json` — dataset loader (confidence 0.90): This file is a dataset for MMLU evaluation, directly relevant to the claim's metric.
- `data/mmlu/zero_shot_mmlu_test.json` — dataset loader (confidence 0.90): This file is a dataset for MMLU evaluation, directly relevant to the claim's metric.

**Missing for this claim:**
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.

**Blockers:**
- Specific MMLU evaluation script and methodology
- Training recipe for 16-bit LoRA baseline for MMLU

### Claim 8

> Guanaco 65B is the best-performing model after GPT-4, achieving 99.3% performance relative to ChatGPT.

**Metric:** performance relative to ChatGPT · proposed 99.3
**Dataset:** Vicuna benchmark
**Method:** Guanaco 65B vs **Baseline:** ChatGPT
**Feasibility:** `medium`

**Evidence:**
> The Vicunabenchmark[10]resultsrelativetoChatGPTareshowninTable6. WefindthatGuanaco 65Bisthebest-performingmodelafterGPT-4,achieving99.3%performancerelativetoChatGPT.

**Code links:**
- `eval/EVAL_README.md` — explanation (confidence 0.46): This README describes the evaluation process using GPT-4 and mentions the Vicuna benchmark queries, which are directly relevant to the claim's evaluation metric and dataset.
- `eval/qa_baseline_gpt.py` — eval script (confidence 0.41): This script is used to generate answers with GPT-3.5/GPT-4, which is a component of the Vicuna benchmark evaluation as described in the paper and `EVAL_README.md`.
- `eval/eval_gpt_review.py` — eval script (confidence 0.37): This script is for evaluating model responses using GPT-4, which is crucial for the Vicuna benchmark and comparing performance to ChatGPT.
- `scripts/finetune_guanaco_65b.sh` — training entry (confidence 0.33): This script shows how to finetune the Guanaco 65B model, which is the subject of this claim.
- `eval/generations/vicuna/65b-guanaco-vicuna-generations-topp0.9-temp0.7.jsonl` — eval data (confidence 0.90): This file contains generated responses for the 65B Guanaco model on the Vicuna benchmark, directly supporting the claim's evaluation.

**Missing for this claim:**
- **[medium] evaluation_script** — The paper describes the evaluation methodology in detail, including the use of GPT-4 for pairwise comparisons and Elo ratings, and human evaluation. However, the actual scripts or code used for these evaluations are not explicitly provided or linked, which would be necessary to replicate the evaluation process precisely.
- **[medium] training_recipe** — While the paper describes the QLoRA method and provides some training hyperparameters, the exact training recipe (e.g., optimizer state initialization, specific learning rate decay schedule if not constant, gradient accumulation steps if used, exact number of training steps/epochs for each model/dataset combination) is not fully specified for all experiments, making exact reproduction challenging.

**Blockers:**
- Full evaluation pipeline for Vicuna benchmark (beyond generation)
- Exact training recipe for Guanaco 65B

## Risks

- Reliance on external APIs (GPT-4) for evaluation, which can be costly and non-deterministic.
- Incomplete evaluation scripts for benchmarks like Vicuna and MMLU, requiring significant reverse-engineering.
- Lack of specific hardware details, making exact reproduction of memory and time claims difficult.
- Absence of full model checkpoints, potentially hindering direct reproduction of finetuned models.

## Next Steps

1. Investigate the full evaluation pipeline for the Vicuna benchmark, specifically how the GPT-4 reviews are processed into a final score.
2. Clarify the exact training recipes (epochs, learning rate schedules, gradient accumulation) for each model size and dataset combination.
3. Identify the specific GPU models used for training and evaluation to better understand hardware constraints.
4. Determine if full model checkpoints (not just adapters) are available or how to reconstruct them for direct reproduction.
