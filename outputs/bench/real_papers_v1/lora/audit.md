# Reproducibility Audit

**Paper id:** `2106.09685`
**Benchmark target:** Reproduce the LoRA fine-tuning of GPT-2 medium on E2E NLG and recover the published BLEU/ROUGE numbers from Table 2.
**Overall feasibility:** `low`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/microsoft__LoRA`
- Important files: README.md, setup.py
- Likely entry points: examples/NLU/src/transformers/commands/train.py, examples/NLU/src/transformers/commands/run.py
- Likely eval scripts: examples/NLU/src/transformers/commands/run.py
- Likely config files: examples/NLU/ds_config.json
- Dependency files: examples/NLU/environment.yml, examples/NLU/pyproject.toml, examples/NLU/setup.py, setup.py
- Has tests: True
- Notes:
  - uses Hydra configs under configs/
  - no requirements file detected

## Overall Missing Details

- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.
- **[medium] training_recipe** — The paper mentions using AdamW optimizer with a linear learning rate decay schedule for most experiments. However, for GPT-3 experiments, it states 'We use the same hyperparameters for all datasets after tuning learning rate.' The specific learning rate schedule and other training recipe details for GPT-3 are not fully specified, which could lead to variations in results.
- **[medium] compute_budget** — The paper mentions using NVIDIA Tesla V100 for RoBERTa and DeBERTa experiments, and NVIDIA Quadro RTX 8000 for latency measurements. However, the specific number of GPUs used for training, the duration of training runs, or the total compute hours for the large-scale GPT-3 experiments are not provided. This makes it difficult to estimate the computational resources required for reproduction.
- **[low] other** — The paper mentions releasing a package that facilitates the integration of LoRA with PyTorch models and provides implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at a GitHub repository. However, the specific version or commit hash of the code is not provided, which could lead to reproducibility issues if the repository is updated.

## Claims Audit

### Claim 1 — _main claim_

> LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times compared to GPT-3 175B fine-tuned with Adam.

**Method:** LoRA vs **Baseline:** Adam fine-tuning
**Feasibility:** `low`

**Evidence:**
> Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times.

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[medium] training_recipe** — The paper mentions using AdamW optimizer with a linear learning rate decay schedule for most experiments. However, for GPT-3 experiments, it states 'We use the same hyperparameters for all datasets after tuning learning rate.' The specific learning rate schedule and other training recipe details for GPT-3 are not fully specified, which could lead to variations in results.
- **[medium] compute_budget** — The paper mentions using NVIDIA Tesla V100 for RoBERTa and DeBERTa experiments, and NVIDIA Quadro RTX 8000 for latency measurements. However, the specific number of GPUs used for training, the duration of training runs, or the total compute hours for the large-scale GPT-3 experiments are not provided. This makes it difficult to estimate the computational resources required for reproduction.

**Blockers:**
- No code for GPT-3 175B fine-tuning or LoRA implementation for GPT-3.
- Lack of specific hyperparameters for GPT-3 experiments.
- No clear indication of how memory usage was measured or optimized in the provided code.

**Notes:** This claim involves GPT-3 175B, which is a very large model. The provided repository focuses on RoBERTa, DeBERTa, and GPT-2. There are no specific scripts or configurations for GPT-3, nor details on how memory reduction was measured.

### Claim 2

> LoRA performs on-par or better than fine-tuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3.

**Method:** LoRA vs **Baseline:** fine-tuning
**Feasibility:** `medium`

**Evidence:**
> LoRA performs on-par or better than fine-tuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3, despite having fewer trainable parameters, a higher training throughput, and, unlike adapters, no additional inference latency.

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.

**Blockers:**
- Lack of explicit LoRA implementation for all mentioned models (especially GPT-3) in the provided code.
- Unclear how 'model quality' is consistently measured across different models and tasks.
- Missing specific dataset splits for GLUE and other benchmarks.

**Notes:** This is a general claim covering multiple models and tasks. While there are scripts for RoBERTa and DeBERTa, the claim also includes GPT-3, for which no specific code is present. The definition of 'on-par or better' is also broad.

### Claim 3

> On RoBERTa base, LoRA achieves an average GLUE score of 87.2, outperforming fine-tuning (86.4) and AdapterD (85.4) with fewer trainable parameters.

**Metric:** Average GLUE score · proposed 87.2
**Dataset:** GLUE benchmark
**Method:** LoRA vs **Baseline:** Fine-Tuning
**Feasibility:** `medium`

**Evidence:**
> RoB (FT)* 125.0M 87.6 94.8 90.2 63.6 92.8 91.9 78.7 91.2 86.4
base
RoB (LoRA) 0.3M 87.5 95.1 89.7 63.4 93.3 90.8 86.6 91.5 87.2
base ±.3 ±.2 ±.7 ±1.2 ±.3 ±.1 ±.7 ±.2

**Code links:**
- `examples/NLU/roberta_base_cola.sh` — training entry (confidence 0.70): This script likely trains a RoBERTa base model on the CoLA dataset, which is part of GLUE. It's a plausible entry point for RoBERTa base experiments.
- `examples/NLU/roberta_base_mnli.sh` — training entry (confidence 0.70): This script likely trains a RoBERTa base model on the MNLI dataset, part of GLUE.
- `examples/NLU/roberta_base_lora_mnli.bin` — other (confidence 0.60): This file name suggests a pre-trained LoRA model for RoBERTa base on MNLI, indicating that LoRA experiments were conducted for RoBERTa base.
- `examples/NLU/src/transformers/data/datasets/glue.py` — dataset loader (confidence 0.90): This file is explicitly named for handling GLUE datasets, which are central to this claim.
- `examples/NLU/src/transformers/data/processors/glue.py` — dataset loader (confidence 0.90): This file is explicitly named for processing GLUE datasets, which are central to this claim.

**Missing for this claim:**
- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.

**Blockers:**
- Specific LoRA configuration for RoBERTa base is not immediately obvious from the file names.
- Exact scripts for fine-tuning and AdapterD baselines for RoBERTa base on GLUE are not clearly identified.
- Missing details on how the 'average GLUE score' is calculated (e.g., which tasks are included, how scores are aggregated).

**Notes:** There are several scripts related to RoBERTa base and GLUE tasks, suggesting that the components for this claim exist. However, the specific LoRA configuration and the exact evaluation script to compute the average GLUE score are not explicitly linked.

### Claim 4

> On RoBERTa large, LoRA achieves an average GLUE score of 89.0, outperforming fine-tuning (88.9) with fewer trainable parameters.

**Metric:** Average GLUE score · proposed 89.0
**Dataset:** GLUE benchmark
**Method:** LoRA vs **Baseline:** Fine-Tuning
**Feasibility:** `medium`

**Evidence:**
> RoB (FT)* 355.0M 90.2 96.4 90.9 68.0 94.7 92.2 86.6 92.4 88.9
large
RoB (LoRA) 0.8M 90.6 96.2 90.9 68.2 94.9 91.6 87.4 92.6 89.0
large ±.2 ±.5 ±1.2 ±1.9 ±.3 ±.1 ±2.5 ±.2

**Code links:**
- `examples/NLU/roberta_large_cola.sh` — training entry (confidence 0.70): This script likely trains a RoBERTa large model on the CoLA dataset, which is part of GLUE. It's a plausible entry point for RoBERTa large experiments.
- `examples/NLU/roberta_large_mnli.sh` — training entry (confidence 0.70): This script likely trains a RoBERTa large model on the MNLI dataset, part of GLUE.
- `examples/NLU/roberta_large_lora_mnli.bin` — other (confidence 0.60): This file name suggests a pre-trained LoRA model for RoBERTa large on MNLI, indicating that LoRA experiments were conducted for RoBERTa large.
- `examples/NLU/adapter_houlsby_roberta_large_mnli.sh` — training entry (confidence 0.60): This script suggests an adapter baseline for RoBERTa large on MNLI, which might be relevant for comparison.
- `examples/NLU/adapter_pfeiffer_roberta_large_mnli.sh` — training entry (confidence 0.60): This script suggests another adapter baseline for RoBERTa large on MNLI, which might be relevant for comparison.
- `examples/NLU/src/transformers/data/datasets/glue.py` — dataset loader (confidence 0.90): This file is explicitly named for handling GLUE datasets, which are central to this claim.
- `examples/NLU/src/transformers/data/processors/glue.py` — dataset loader (confidence 0.90): This file is explicitly named for processing GLUE datasets, which are central to this claim.

**Missing for this claim:**
- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.

**Blockers:**
- Specific LoRA configuration for RoBERTa large is not immediately obvious from the file names.
- Exact scripts for fine-tuning baseline for RoBERTa large on GLUE are not clearly identified.
- Missing details on how the 'average GLUE score' is calculated (e.g., which tasks are included, how scores are aggregated).

**Notes:** Similar to claim 2, there are scripts for RoBERTa large and GLUE tasks. The presence of adapter scripts also suggests a comparison framework. However, the precise LoRA configuration and evaluation method for the average GLUE score need to be identified.

### Claim 5

> On DeBERTa XXL, LoRA achieves an average GLUE score of 91.3, compared to fine-tuning's 91.1.

**Metric:** Average GLUE score · proposed 91.3
**Dataset:** GLUE benchmark
**Method:** LoRA vs **Baseline:** Fine-Tuning
**Feasibility:** `medium`

**Evidence:**
> DeB (FT)* 1500.0M 91.8 97.2 92.0 72.0 96.0 92.7 93.9 92.9 91.1
XXL
DeB (LoRA) 4.7M 91.9 96.9 92.6 72.4 96.0 92.9 94.9 93.0 91.3
XXL ±.2 ±.2 ±.6 ±1.1 ±.1 ±.1 ±.4 ±.2

**Code links:**
- `examples/NLU/deberta_v2_xxlarge_cola.sh` — training entry (confidence 0.70): This script likely trains a DeBERTa XXL model on the CoLA dataset, which is part of GLUE. It's a plausible entry point for DeBERTa XXL experiments.
- `examples/NLU/deberta_v2_xxlarge_mnli.sh` — training entry (confidence 0.70): This script likely trains a DeBERTa XXL model on the MNLI dataset, part of GLUE.
- `examples/NLU/src/transformers/data/datasets/glue.py` — dataset loader (confidence 0.90): This file is explicitly named for handling GLUE datasets, which are central to this claim.
- `examples/NLU/src/transformers/data/processors/glue.py` — dataset loader (confidence 0.90): This file is explicitly named for processing GLUE datasets, which are central to this claim.

**Missing for this claim:**
- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.

**Blockers:**
- Specific LoRA configuration for DeBERTa XXL is not immediately obvious from the file names.
- Exact scripts for fine-tuning baseline for DeBERTa XXL on GLUE are not clearly identified.
- Missing details on how the 'average GLUE score' is calculated (e.g., which tasks are included, how scores are aggregated).

**Notes:** Scripts for DeBERTa XXL on various GLUE tasks are present. However, the specific LoRA implementation for DeBERTa XXL and the evaluation method for the average GLUE score need to be confirmed.

### Claim 6

> On the E2E NLG Challenge, GPT-2M (LoRA) with 0.35M trainable parameters achieves a BLEU score of 70.4, outperforming GPT-2M (FT) with 354.92M parameters (68.2).

**Metric:** BLEU · proposed 70.4
**Dataset:** E2E NLG Challenge
**Method:** GPT-2M (LoRA) vs **Baseline:** GPT-2M (FT)
**Feasibility:** `medium`

**Evidence:**
> GPT-2M(FT)* 354.92M 68.2 8.62 46.2 71.0 2.47
GPT-2M(LoRA) 0.35M 70.4 8.85 46.8 71.8 2.53
±.1 ±.02 ±.2 ±.1 ±.02

**Code links:**
- `examples/NLG/README.md` — other (confidence 0.80): The presence of an 'NLG' (Natural Language Generation) directory and a README within it strongly suggests that experiments related to NLG tasks like E2E NLG were conducted here.
- `examples/NLG/requirement.txt` — dependency file (confidence 0.70): This file would list dependencies specific to the NLG examples, which would include the E2E NLG Challenge.
- `examples/NLG/create_datasets.sh` — dataset loader (confidence 0.70): This script likely handles the preparation of datasets for NLG tasks, potentially including the E2E NLG Challenge.

**Missing for this claim:**
- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.
- **[medium] training_recipe** — The paper mentions using AdamW optimizer with a linear learning rate decay schedule for most experiments. However, for GPT-3 experiments, it states 'We use the same hyperparameters for all datasets after tuning learning rate.' The specific learning rate schedule and other training recipe details for GPT-3 are not fully specified, which could lead to variations in results.

**Blockers:**
- No explicit training script for GPT-2M (LoRA) or GPT-2M (FT) on E2E NLG is found in the provided file list.
- No clear evaluation script for BLEU score on E2E NLG is identified.
- Specific LoRA configuration for GPT-2M is not evident.
- The E2E NLG dataset itself is not directly present, though a `create_datasets.sh` exists.

**Notes:** The presence of an `examples/NLG` directory is promising, but specific scripts for GPT-2M LoRA fine-tuning and evaluation on E2E NLG are not directly visible. The `requirement.txt` and `create_datasets.sh` suggest that the environment and data preparation for NLG tasks are handled.

### Claim 7

> On the E2E NLG Challenge, GPT-2L (LoRA) with 0.77M trainable parameters achieves a BLEU score of 70.4, outperforming GPT-2L (FT) with 774.03M parameters (68.5).

**Metric:** BLEU · proposed 70.4
**Dataset:** E2E NLG Challenge
**Method:** GPT-2L (LoRA) vs **Baseline:** GPT-2L (FT)
**Feasibility:** `medium`

**Evidence:**
> GPT-2L(FT)* 774.03M 68.5 8.78 46.0 69.9 2.45
GPT-2L(LoRA) 0.77M 70.4 8.89 46.8 72.0 2.47
±.1 ±.02 ±.2 ±.2 ±.02

**Code links:**
- `examples/NLG/README.md` — other (confidence 0.80): The presence of an 'NLG' (Natural Language Generation) directory and a README within it strongly suggests that experiments related to NLG tasks like E2E NLG were conducted here.
- `examples/NLG/requirement.txt` — dependency file (confidence 0.70): This file would list dependencies specific to the NLG examples, which would include the E2E NLG Challenge.
- `examples/NLG/create_datasets.sh` — dataset loader (confidence 0.70): This script likely handles the preparation of datasets for NLG tasks, potentially including the E2E NLG Challenge.

**Missing for this claim:**
- **[high] data_split** — The paper mentions using the GLUE benchmark and other datasets, but does not specify the exact train/validation/test splits used for each dataset. This is crucial for reproducing the reported results, especially for tasks like MNLI where different splits can lead to different performance metrics.
- **[medium] hyperparameters** — While the paper provides hyperparameters for RoBERTa, DeBERTa, and GPT-2 in the appendices, it states for GPT-3 experiments that 'We tune learning rate for all method-dataset combinations.' However, the specific learning rates and other tuned hyperparameters for GPT-3 are not fully detailed, making it difficult to reproduce the GPT-3 results precisely.
- **[medium] training_recipe** — The paper mentions using AdamW optimizer with a linear learning rate decay schedule for most experiments. However, for GPT-3 experiments, it states 'We use the same hyperparameters for all datasets after tuning learning rate.' The specific learning rate schedule and other training recipe details for GPT-3 are not fully specified, which could lead to variations in results.

**Blockers:**
- No explicit training script for GPT-2L (LoRA) or GPT-2L (FT) on E2E NLG is found in the provided file list.
- No clear evaluation script for BLEU score on E2E NLG is identified.
- Specific LoRA configuration for GPT-2L is not evident.
- The E2E NLG dataset itself is not directly present, though a `create_datasets.sh` exists.

**Notes:** Similar to claim 5, the `examples/NLG` directory suggests relevant work, but specific scripts for GPT-2L LoRA fine-tuning and evaluation on E2E NLG are not directly visible. The `requirement.txt` and `create_datasets.sh` indicate that the environment and data preparation for NLG tasks are handled.

### Claim 8

> On GPT-3 175B, LoRA with 4.7M trainable parameters achieves 73.4% accuracy on WikiSQL, outperforming full fine-tuning (73.8%) and AdapterH (71.9%).

**Metric:** WikiSQL accuracy · proposed 73.4
**Dataset:** WikiSQL (split: validation)
**Method:** GPT-3(LoRA) vs **Baseline:** GPT-3(FT)
**Feasibility:** `low`

**Evidence:**
> GPT-3(FT) 175,255.8M 73.8 89.5 52.0/28.0/44.5
GPT-3(LoRA) 4.7M 73.4 91.7 53.8/29.8/45.9

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[medium] training_recipe** — The paper mentions using AdamW optimizer with a linear learning rate decay schedule for most experiments. However, for GPT-3 experiments, it states 'We use the same hyperparameters for all datasets after tuning learning rate.' The specific learning rate schedule and other training recipe details for GPT-3 are not fully specified, which could lead to variations in results.
- **[medium] compute_budget** — The paper mentions using NVIDIA Tesla V100 for RoBERTa and DeBERTa experiments, and NVIDIA Quadro RTX 8000 for latency measurements. However, the specific number of GPUs used for training, the duration of training runs, or the total compute hours for the large-scale GPT-3 experiments are not provided. This makes it difficult to estimate the computational resources required for reproduction.

**Blockers:**
- No code for GPT-3 175B fine-tuning or LoRA implementation for GPT-3.
- Lack of specific hyperparameters for GPT-3 experiments.
- No clear indication of how WikiSQL accuracy was measured.
- The WikiSQL dataset is not mentioned or handled in the provided file list.

**Notes:** This claim involves GPT-3 175B and the WikiSQL dataset. There are no specific scripts or configurations for GPT-3 or WikiSQL in the provided repository. This makes reproduction of this claim highly challenging.

## Risks

- Lack of explicit LoRA implementation details for all models (especially GPT-3).
- Missing specific dataset splits and preprocessing steps for various benchmarks.
- Absence of clear evaluation scripts for reported metrics (e.g., average GLUE score, BLEU, ROUGE, WikiSQL accuracy).
- Incomplete hyperparameter details for GPT-3 experiments.
- The repository seems to be a general Transformers library, not specifically tailored to the LoRA paper's experiments, making it hard to pinpoint exact reproduction steps.

## Next Steps

1. Identify the exact LoRA implementation within the `src/transformers/models` directory, if it exists, and how it's integrated into the training scripts.
2. Examine the `examples/NLU` and `examples/NLG` directories more deeply for specific training and evaluation scripts that use LoRA and target the mentioned datasets.
3. Look for configuration files (e.g., YAML, JSON) that specify LoRA parameters and model architectures.
4. Search for any `README` files within the `examples` subdirectories that might provide more detailed instructions for reproducing specific claims.
5. Investigate how the 'average GLUE score' is computed and if there's a unified evaluation script for it.
