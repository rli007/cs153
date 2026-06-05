# Reproducibility Audit

**Paper id:** `2205.14135`
**Benchmark target:** Reproduce the FlashAttention end-to-end speedup on GPT-2 training reported in Table 1.
**Overall feasibility:** `low`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/Dao-AILab__flash-attention`
- Important files: README.md, setup.py, Makefile
- Likely entry points: none detected
- Likely eval scripts: none detected
- Likely config files: benchmarks/configs/clc.yaml, training/configs/config.yaml
- Dependency files: flash_attn/cute/pyproject.toml, flash_attn/pyproject.toml, hopper/setup.py, setup.py, tests/pyproject.toml
- Has tests: True
- Notes:
  - uses Hydra configs under training/configs/
  - FlashAttention-4 (FA4) is the active development branch in flash_attn/cute/
  - Hopper (FA3) related files in hopper/ directory

## Overall Missing Details

- **[medium] random_seed** — The random seeds used for training are not specified. This is crucial for reproducing the exact model weights and performance, especially for experiments involving dropout or other stochastic elements.
- **[medium] hardware** — While the paper mentions using A100 GPUs and RTX 3090/T4 for benchmarking, the specific configurations (e.g., number of GPUs, interconnects, CPU model, RAM) for the training experiments (BERT, GPT-2, LRA) are not fully detailed. This could lead to variations in reported training times.
- **[medium] data_split** — While the paper mentions using specific datasets (Wikipedia, OpenWebText, MIMIC-III, ECtHR, LRA benchmarks), the exact splits for training, validation, and testing are not always explicitly stated. For example, for OpenWebText, it's mentioned that 0.5% is randomly selected for validation, but the seed for this split is not provided.
- **[medium] hyperparameters** — While some hyperparameters are mentioned (e.g., optimizer, learning rate, weight decay for GPT-2, LAMB optimizer for BERT), many details are missing for the training of the models on specific tasks. For instance, the exact learning rate schedule, dropout rates for different layers, and specific hyperparameters for the LRA tasks (beyond referencing other papers) are not fully specified.
- **[high] checkpoint** — The paper does not specify if or how model checkpoints were saved and loaded during training, nor does it provide access to any pre-trained checkpoints. This is essential for reproducing the exact final model weights.
- **[medium] evaluation_script** — While the paper reports results on various benchmarks and tasks, the exact scripts or code used for evaluation are not provided. This includes details on how metrics like accuracy, perplexity, and F1-score were computed.
- **[medium] data_preprocessing** — Details on data preprocessing steps, such as tokenization (beyond mentioning GPT-2 BPE tokenizer), text cleaning, or any specific transformations applied to the datasets, are not fully described. This can impact reproducibility, especially for NLP tasks.
- **[medium] training_recipe** — While some aspects of the training recipe are mentioned (e.g., optimizer, learning rate, batch size, number of steps/epochs), a complete recipe for each experiment is not provided. This includes details like learning rate schedules, gradient clipping, weight initialization strategies, and specific training configurations for each benchmark.
- **[low] license** — The license under which the FlashAttention code is released is not explicitly stated in the paper. While a GitHub link is provided, the license information is crucial for understanding the terms of use and redistribution.
- **[low] compute_budget** — While training times are reported for specific experiments (e.g., BERT, GPT-2), a comprehensive compute budget (e.g., total FLOPs, GPU hours) for each major experiment is not provided. This would help in understanding the scale of the experiments and comparing them to other research.
- **[low] other** — The paper mentions using Apex's FMHA code as a starting point and provides a link. However, the specific version or commit hash of the Apex FMHA code used is not specified, which could lead to minor differences in implementation details.

## Claims Audit

### Claim 1 — _main claim_

> FlashAttention trains BERT-large (seq. length 512) 15% faster than the MLPerf 1.1 training speed record.

**Metric:** end-to-end wall-clock speedup · proposed 1.15
**Method:** FlashAttention vs **Baseline:** MLPerf 1.1 training speed record
**Feasibility:** `low`

**Evidence:**
> FlashAttention trains Transformer models faster in wall-clock time. We train BERT-large (seq. length 512) 15% faster than the training speed record in MLPerf 1.1 [58], GPT2 (seq. length 1K) 3× faster than baseline implementations from HuggingFace [87] and Megatron-LM [77], and long-range arena (seq. length 1K-4K) 2.4× faster than baselines.

**Code links:**
- `flash_attn/models/bert.py` — training entry (confidence 0.70): This file likely contains the BERT model definition and could be used for training. The claim is about BERT-large training speed.
- `benchmarks/benchmark_flash_attention.py` — eval script (confidence 0.60): This script is a general benchmark for FlashAttention and might be adapted to measure BERT training speed.
- `benchmarks/configs/clc.yaml` — configs (confidence 0.40): This is a configuration file for benchmarks, but its direct relevance to BERT-large training speed is unclear without more context.

**Missing for this claim:**
- **[high] training_recipe** — The specific training recipe for BERT-large (e.g., optimizer, learning rate schedule, batch size, number of steps/epochs) is not provided, making it difficult to reproduce the reported training speed.
- **[medium] hardware** — The specific hardware configuration (e.g., number of GPUs, interconnects, CPU model, RAM) used for the BERT-large training speed benchmark is not fully detailed.
- **[medium] data_preprocessing** — Details on data preprocessing steps for BERT-large training are not described.
- **[medium] other** — The exact MLPerf 1.1 training speed record configuration and how it was measured for comparison are not detailed.

**Blockers:**
- Missing complete BERT-large training recipe
- Unclear how MLPerf 1.1 baseline was established
- Lack of specific hardware configuration

**Notes:** Reproducing a speedup against an external benchmark like MLPerf 1.1 requires precise replication of both the proposed method and the baseline, which is not fully supported by the provided information.

### Claim 2

> FlashAttention trains GPT-2 (seq. length 1K) 3× faster than baseline implementations from HuggingFace and Megatron-LM.

**Metric:** end-to-end wall-clock speedup · proposed 3.0
**Method:** FlashAttention vs **Baseline:** HuggingFace and Megatron-LM implementations
**Feasibility:** `low`

**Evidence:**
> FlashAttention trains Transformer models faster in wall-clock time. We train BERT-large (seq. length 512) 15% faster than the training speed record in MLPerf 1.1 [58], GPT2 (seq. length 1K) 3× faster than baseline implementations from HuggingFace [87] and Megatron-LM [77], and long-range arena (seq. length 1K-4K) 2.4× faster than baselines.

**Code links:**
- `flash_attn/models/gpt.py` — training entry (confidence 0.80): This file likely contains the GPT model definition, which would be used for GPT-2 training.
- `assets/gpt2_training_efficiency.jpg` — other (confidence 0.70): This asset directly relates to GPT-2 training efficiency, suggesting that the code to generate such data exists.
- `benchmarks/benchmark_flash_attention.py` — eval script (confidence 0.60): This script is a general benchmark for FlashAttention and could be used to measure GPT-2 training speed.
- `training/configs/config.yaml` — configs (confidence 0.50): This is a general configuration file for training and might contain GPT-2 specific settings.

**Missing for this claim:**
- **[high] training_recipe** — A complete training recipe for GPT-2, including specific hyperparameters, learning rate schedule, and dataset details, is not provided.
- **[medium] hardware** — The specific hardware configuration used for GPT-2 training benchmarks is not fully detailed.
- **[high] other** — The exact configurations and versions of HuggingFace and Megatron-LM implementations used as baselines are not specified, making direct comparison difficult.
- **[medium] data_preprocessing** — Details on data preprocessing steps for GPT-2 training are not described.

**Blockers:**
- Missing complete GPT-2 training recipe
- Unspecified baseline implementations (HuggingFace, Megatron-LM)
- Lack of specific hardware configuration

**Notes:** While there are indications of GPT-2 training, the lack of a full training recipe and specific baseline details makes direct reproduction of the speedup challenging.

### Claim 3

> FlashAttention speeds up the long-range arena (LRA) benchmark (seq. length 1K-4K) 2.4× compared to baselines.

**Metric:** speedup · proposed 2.4
**Dataset:** long-range arena
**Method:** FlashAttention vs **Baseline:** baselines
**Feasibility:** `low`

**Evidence:**
> FlashAttention trains Transformer models faster in wall-clock time. We train BERT-large (seq. length 512) 15% faster than the training speed record in MLPerf 1.1 [58], GPT2 (seq. length 1K) 3× faster than baseline implementations from HuggingFace [87] and Megatron-LM [77], and long-range arena (seq. length 1K-4K) 2.4× faster than baselines.

**Code links:**
- `benchmarks/benchmark_flash_attention.py` — eval script (confidence 0.70): This script is a general benchmark for FlashAttention and could be used to measure speedup on LRA tasks.
- `benchmarks/configs/clc.yaml` — configs (confidence 0.40): This is a configuration file for benchmarks, but its direct relevance to LRA is unclear without more context.

**Missing for this claim:**
- **[high] training_recipe** — The specific training recipes and evaluation procedures for the Long-Range Arena (LRA) benchmark tasks are not provided.
- **[medium] data_split** — The exact data splits and preprocessing for the LRA benchmark are not detailed.
- **[high] other** — The specific 'baselines' used for comparison on LRA are not identified, making it impossible to reproduce the speedup.
- **[medium] hardware** — The specific hardware configuration used for LRA benchmarks is not fully detailed.

**Blockers:**
- Missing LRA training/evaluation recipes
- Unspecified baselines for LRA
- Lack of specific hardware configuration

**Notes:** The LRA benchmark involves multiple tasks, and the paper does not provide sufficient details to reproduce the reported speedup across them.

### Claim 4

> FlashAttention achieves 0.7 better perplexity on GPT-2.

**Metric:** perplexity · delta 0.7
**Dataset:** GPT-2
**Method:** FlashAttention vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> FlashAttention and block-sparse FlashAttention enable longer context in Transformers, yielding higher quality models (0.7 better perplexity on GPT-2 and 6.4 points of lift on long-document classification) and entirely new capabilities: the first Transformers to achieve better-than-chance performance on the Path-X challenge (seq. length 16K, 61.4% accuracy) and Path-256 (seq. length 64K, 63.1% accuracy).

**Code links:**
- `flash_attn/models/gpt.py` — training entry (confidence 0.80): This file likely contains the GPT model definition, which would be used for GPT-2 training and perplexity evaluation.
- `assets/gpt2_training_curve.jpg` — other (confidence 0.70): This asset shows a GPT-2 training curve, which would include perplexity metrics.
- `flash_attn/losses/cross_entropy.py` — eval script (confidence 0.60): Perplexity is typically derived from cross-entropy loss, so this file might be involved in its calculation.
- `training/configs/config.yaml` — configs (confidence 0.50): This is a general configuration file for training and might contain GPT-2 specific settings relevant to perplexity.

**Missing for this claim:**
- **[high] training_recipe** — A complete training recipe for GPT-2, including specific hyperparameters, learning rate schedule, and dataset details, is not provided. This is crucial for achieving a specific perplexity.
- **[medium] data_split** — The exact data splits (training, validation, test) and preprocessing for GPT-2 are not fully detailed, which can significantly impact perplexity results.
- **[medium] evaluation_script** — The exact script or method used to calculate perplexity on GPT-2 is not provided.
- **[medium] hardware** — The specific hardware configuration used for GPT-2 training and evaluation is not fully detailed.

**Blockers:**
- Missing complete GPT-2 training recipe
- Unspecified data splits and preprocessing for GPT-2
- Lack of explicit perplexity evaluation script

**Notes:** Achieving a specific perplexity value requires precise replication of the training setup, which is not adequately detailed.

### Claim 5

> FlashAttention yields 6.4 points of lift on long-document classification.

**Metric:** lift · delta 6.4
**Dataset:** long-document classification
**Method:** FlashAttention vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> FlashAttention and block-sparse FlashAttention enable longer context in Transformers, yielding higher quality models (0.7 better perplexity on GPT-2 and 6.4 points of lift on long-document classification) and entirely new capabilities: the first Transformers to achieve better-than-chance performance on the Path-X challenge (seq. length 16K, 61.4% accuracy) and Path-256 (seq. length 64K, 63.1% accuracy).

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[high] training_recipe** — The specific training recipe for long-document classification, including model architecture, hyperparameters, and training procedure, is not provided.
- **[high] data_split** — The specific dataset, its splits, and preprocessing steps for long-document classification are not detailed.
- **[high] evaluation_script** — The exact script or method used to calculate 'lift' on long-document classification is not provided.
- **[high] other** — The baseline against which the 6.4 points of lift are measured is not specified.
- **[medium] hardware** — The specific hardware configuration used for long-document classification experiments is not fully detailed.

**Blockers:**
- Missing training recipe for long-document classification
- Unspecified dataset and preprocessing
- Unspecified baseline for lift calculation
- Lack of evaluation script

**Notes:** This claim lacks almost all necessary details for reproduction, including the specific task, dataset, model, and baseline.

### Claim 6

> FlashAttention achieves 61.4% accuracy on the Path-X challenge (seq. length 16K).

**Metric:** accuracy · proposed 61.4
**Dataset:** Path-X
**Method:** FlashAttention vs **Baseline:** chance
**Feasibility:** `low`

**Evidence:**
> FlashAttention and block-sparse FlashAttention enable longer context in Transformers, yielding higher quality models (0.7 better perplexity on GPT-2 and 6.4 points of lift on long-document classification) and entirely new capabilities: the first Transformers to achieve better-than-chance performance on the Path-X challenge (seq. length 16K, 61.4% accuracy) and Path-256 (seq. length 64K, 63.1% accuracy).

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[high] training_recipe** — The specific training recipe for the Path-X challenge, including model architecture, hyperparameters, and training procedure, is not provided.
- **[high] data_split** — The specific dataset, its splits, and preprocessing steps for the Path-X challenge are not detailed.
- **[high] evaluation_script** — The exact script or method used to calculate accuracy on the Path-X challenge is not provided.
- **[medium] hardware** — The specific hardware configuration used for Path-X challenge experiments is not fully detailed.

**Blockers:**
- Missing training recipe for Path-X
- Unspecified dataset and preprocessing for Path-X
- Lack of evaluation script for Path-X

**Notes:** Similar to claim 4, this claim lacks sufficient detail for reproduction. The Path-X challenge itself is not explicitly referenced in the repo.

### Claim 7

> Block-sparse FlashAttention achieves 63.1% accuracy on Path-256 (seq. length 64K).

**Metric:** accuracy · proposed 63.1
**Dataset:** Path-256
**Method:** Block-sparse FlashAttention vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> FlashAttention and block-sparse FlashAttention enable longer context in Transformers, yielding higher quality models (0.7 better perplexity on GPT-2 and 6.4 points of lift on long-document classification) and entirely new capabilities: the first Transformers to achieve better-than-chance performance on the Path-X challenge (seq. length 16K, 61.4% accuracy) and Path-256 (seq. length 64K, 63.1% accuracy).

**Code links:**
- `flash_attn/flash_blocksparse_attention.py` — training entry (confidence 0.80): This file implements block-sparse attention, which is the method used in this claim.
- `flash_attn/cute/block_sparse_utils.py` — other (confidence 0.70): This file contains utilities for block-sparse operations, directly relevant to the claim.

**Missing for this claim:**
- **[high] training_recipe** — The specific training recipe for Path-256 using Block-sparse FlashAttention, including model architecture, hyperparameters, and training procedure, is not provided.
- **[high] data_split** — The specific dataset, its splits, and preprocessing steps for Path-256 are not detailed.
- **[high] evaluation_script** — The exact script or method used to calculate accuracy on Path-256 is not provided.
- **[medium] hardware** — The specific hardware configuration used for Path-256 experiments is not fully detailed.

**Blockers:**
- Missing training recipe for Path-256 with block-sparse attention
- Unspecified dataset and preprocessing for Path-256
- Lack of evaluation script for Path-256

**Notes:** While the code for block-sparse attention exists, the specific application to Path-256 with a full training and evaluation setup is missing.

### Claim 8

> FlashAttention is up to 7.6x faster on the attention computation on GPT-2 compared to PyTorch.

**Metric:** speedup · proposed 7.6
**Dataset:** GPT-2
**Method:** FlashAttention vs **Baseline:** PyTorch implementation
**Feasibility:** `medium`

**Evidence:**
> FlashAttention does not read and write the large 𝑁 ×𝑁 attention matrix to HBM, resulting in an 7.6× speedup on the attention computation.

**Code links:**
- `benchmarks/benchmark_attn.py` — eval script (confidence 0.90): This file is specifically designed to benchmark attention mechanisms, which directly relates to the claim of speedup in attention computation.
- `benchmarks/benchmark_flash_attention.py` — eval script (confidence 0.80): This is a general FlashAttention benchmark and would likely include attention computation speed measurements.
- `flash_attn/flash_attn_interface.py` — training entry (confidence 0.70): This file provides the interface for FlashAttention, which would be benchmarked.
- `flash_attn/models/gpt.py` — other (confidence 0.60): This file defines the GPT model, providing context for the 'GPT-2' part of the claim, even if the benchmark is on the attention component.

**Missing for this claim:**
- **[medium] hardware** — The specific hardware configuration (e.g., GPU model, driver version) used for the attention computation benchmark is not fully detailed.
- **[medium] other** — The specific PyTorch implementation of attention used as a baseline for comparison is not detailed (e.g., standard `torch.nn.MultiheadAttention` or a custom implementation).
- **[low] hyperparameters** — Specific parameters for the attention computation benchmark (e.g., sequence length, head dimension, batch size) are not explicitly stated for the 7.6x speedup claim, though some might be inferred from GPT-2 context.

**Blockers:**
- Unspecified PyTorch baseline implementation
- Lack of specific hardware configuration details

**Notes:** The presence of dedicated benchmarking scripts for attention makes this claim more feasible than others, but details on the baseline and hardware are still needed.

## Risks

- Lack of complete training recipes for all models (BERT, GPT-2, LRA, etc.)
- Unspecified baseline implementations for comparisons (MLPerf, HuggingFace, Megatron-LM, PyTorch, 'baselines')
- Missing specific hardware configurations for benchmarks and training
- Absence of explicit evaluation scripts for reported metrics (perplexity, accuracy, lift)
- Incomplete data preprocessing and splitting details for various datasets

## Next Steps

1. Request full training scripts and configuration files for BERT-large and GPT-2.
2. Clarify the exact versions and configurations of baseline implementations (HuggingFace, Megatron-LM, PyTorch) used for speed comparisons.
3. Obtain detailed hardware specifications (GPU model, number of GPUs, interconnect, CPU, RAM) for all reported benchmarks.
4. Request explicit evaluation scripts for perplexity, accuracy, and 'lift' metrics.
5. Seek detailed data preprocessing steps and data splits for all datasets mentioned (OpenWebText, LRA, Path-X, Path-256).
