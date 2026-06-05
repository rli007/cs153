# Reproducibility Audit

**Paper id:** `2205.14135`
**Benchmark target:** Reproduce the FlashAttention end-to-end speedup on GPT-2 training reported in Table 1.
**Overall feasibility:** `medium`

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
  - FlashAttention-4 is the active development branch in flash_attn/cute/
  - Hopper/FA3 kernels are in hopper/ directory
  - Benchmarks use configs in benchmarks/configs/

## Overall Missing Details

- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[low] compute_budget** — The paper reports training times in days or hours for specific models and hardware configurations (e.g., 2.7 days for GPT-2 small with FlashAttention on 8xA100 GPUs). However, it does not provide a comprehensive compute budget (e.g., total FLOPs, GPU hours) for the reported experiments, which would be useful for understanding the scale of computation involved.
- **[low] hardware** — While the paper mentions using A100 GPUs for most experiments and provides some speedup comparisons on RTX 3090 and T4, it does not explicitly state the exact GPU model (e.g., A100-40GB vs A100-80GB) for all experiments, especially when reporting training times for BERT and GPT-2. The specific configuration of the 8x GPU setup (e.g., interconnect) is also not detailed.
- **[medium] data_preprocessing** — The paper mentions using the GPT-2 BPE tokenizer for OpenWebText and repeating positional embeddings for long documents. However, it does not detail the specific preprocessing steps for other datasets like MIMIC-III, ECtHR, or the LRA benchmark tasks, nor does it specify any tokenization or normalization procedures beyond the standard ones implied by the model architectures.
- **[medium] random_seed** — The paper mentions averaging results over 10 runs for BERT training, but does not specify if a fixed random seed was used for each run or if the runs were independent with different seeds. For other experiments, the use of random seeds is not mentioned.

## Claims Audit

### Claim 1 — _main claim_

> FlashAttention trains BERT-large (seq. length 512) 15% faster than the MLPerf 1.1 training speed record.

**Metric:** end-to-end wall-clock speedup · proposed 1.15
**Method:** FlashAttention vs **Baseline:** MLPerf 1.1 training speed record
**Feasibility:** `medium`

**Evidence:**
> FlashAttention trains Transformers faster than existing baselines: 15% end-to-end wall-clock speedup on BERT-large (seq. length 512) compared to the MLPerf 1.1 training speed record, 3× speedup on GPT-2 (seq. length 1K), and 2.4× speedup on long-range arena (seq. length 1K-4K). _(Page 1)_
> Our implementation is 15% faster. _(Page 7)_

**Code links:**
- `README.md` — rationale (confidence 0.68): The README directly references the MLPerf 2.0 benchmark and an IEEE Spectrum article about FlashAttention's submission, indicating its relevance to MLPerf speed records.
- `flash_attn/models/bert.py` — training entry (confidence 0.59): This file explicitly states that the BERT implementation is based on MLPerf 2.0 and 2.1 BERT implementations, suggesting it's the code used for BERT training benchmarks.
- `flash_attn/bert_padding.py` — utility (confidence 0.57): This file contains utilities for BERT padding, which would be used during BERT training.
- `flash_attn/flash_blocksparse_attention.py` — component (confidence 0.57): This file implements FlashBlocksparseAttention, which could be a component used in BERT training for efficiency.
- `flash_attn/models/bert.py` — training entry (confidence 0.56): This section of the BERT model file defines the pre-training output, which is essential for the training process.
- `training/README.md` — documentation (confidence 0.56): The training README provides context on speedups and mentions GPT3, which is related to large language model training, similar to BERT.

**Missing for this claim:**
- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[low] hardware** — While the paper mentions using A100 GPUs for most experiments and provides some speedup comparisons on RTX 3090 and T4, it does not explicitly state the exact GPU model (e.g., A100-40GB vs A100-80GB) for all experiments, especially when reporting training times for BERT and GPT-2. The specific configuration of the 8x GPU setup (e.g., interconnect) is also not detailed.
- **[medium] random_seed** — The paper mentions averaging results over 10 runs for BERT training, but does not specify if a fixed random seed was used for each run or if the runs were independent with different seeds. For other experiments, the use of random seeds is not mentioned.

**Blockers:**
- Specific MLPerf 1.1 training speed record details for comparison
- Exact BERT-large configuration and training script for the reported speedup
- Full training hyperparameters for BERT-large
- Data preprocessing steps for BERT-large

**Notes:** The repo contains BERT model code and references MLPerf, but a direct, executable script to reproduce the specific MLPerf speedup claim is not immediately obvious. The `training/` directory might contain relevant scripts, but they are not explicitly linked to this claim.

### Claim 2

> FlashAttention trains GPT-2 (seq. length 1K) 3x faster than baseline implementations from HuggingFace and Megatron-LM.

**Metric:** end-to-end wall-clock speedup · proposed 3.0
**Method:** FlashAttention vs **Baseline:** HuggingFace and Megatron-LM implementations
**Feasibility:** `medium`

**Evidence:**
> FlashAttention trains Transformers faster than existing baselines: 15% end-to-end wall-clock speedup on BERT-large (seq. length 512) compared to the MLPerf 1.1 training speed record, 3× speedup on GPT-2 (seq. length 1K), and 2.4× speedup on long-range arena (seq. length 1K-4K). _(Page 1)_
> Table 2 shows up to 3× end-to-end speedup compared to Huggingface and 1.7× speedup compared to Megatron-LM. _(Page 7)_

**Code links:**
- `training/README.md` — documentation (confidence 0.73): The training README explicitly states 'The implementation in this repo (FlashAttention) is 3-5x faster than the baseline implementation from Huggingface' and mentions GPT3, which is closely related to GPT-2 training.
- `README.md` — documentation (confidence 0.64): The main README mentions FlashAttention's benefits and links to the training script, which is relevant for GPT-2 training.
- `README.md` — documentation (confidence 0.58): This section of the README directly discusses speedups for training GPT2 and GPT3 compared to Huggingface baselines, matching the claim's context.
- `flash_attn/cute/flash_fwd_sm120.py` — component (confidence 0.56): This file is part of the FlashAttention implementation for forward pass, which would be used in GPT-2 training.
- `flash_attn/cute/flash_bwd_sm120.py` — component (confidence 0.54): This file is part of the FlashAttention implementation for backward pass, which would be used in GPT-2 training.
- `training/README.md` — documentation (confidence 0.53): The training README provides an overview of the optimized Transformer implementation and its speedups, directly relevant to the claim.

**Missing for this claim:**
- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[low] hardware** — While the paper mentions using A100 GPUs for most experiments and provides some speedup comparisons on RTX 3090 and T4, it does not explicitly state the exact GPU model (e.g., A100-40GB vs A100-80GB) for all experiments, especially when reporting training times for BERT and GPT-2. The specific configuration of the 8x GPU setup (e.g., interconnect) is also not detailed.
- **[medium] random_seed** — The paper mentions averaging results over 10 runs for BERT training, but does not specify if a fixed random seed was used for each run or if the runs were independent with different seeds. For other experiments, the use of random seeds is not mentioned.

**Blockers:**
- Specific training scripts for GPT-2 with FlashAttention and baselines (HuggingFace, Megatron-LM)
- Exact configurations for GPT-2 (e.g., model size, number of layers, heads)
- Details on how baseline implementations were run and measured
- Data loading and preprocessing for OpenWebText

**Notes:** The `training/` directory is indicated as containing scripts for GPT-2 training. However, the exact scripts for reproducing the speedup comparison against HuggingFace and Megatron-LM are not explicitly identified, nor are the specific configurations for GPT-2.

### Claim 3

> FlashAttention speeds up the long-range arena (seq. length 1K-4K) 2.4x compared to baselines.

**Metric:** speedup · proposed 2.4
**Dataset:** long-range arena
**Method:** FlashAttention vs **Baseline:** baselines
**Feasibility:** `low`

**Evidence:**
> FlashAttention trains Transformers faster than existing baselines: 15% end-to-end wall-clock speedup on BERT-large (seq. length 512) compared to the MLPerf 1.1 training speed record, 3× speedup on GPT-2 (seq. length 1K), and 2.4× speedup on long-range arena (seq. length 1K-4K). _(Page 1)_
> FlashAttention achieves up 2.4× speed-up compared to standard attention. _(Page 7)_

**Code links:**
- `README.md` — documentation (confidence 0.65): The main README introduces FlashAttention and its benefits, which would include performance on benchmarks like LRA.
- `training/README.md` — documentation (confidence 0.51): The training README discusses speedups and mentions GPT3, which is related to large sequence length models, relevant for LRA.
- `flash_attn/flash_attn_interface.py` — component (confidence 0.49): This file defines the core FlashAttention function, which would be used for LRA benchmarks.
- `training/README.md` — documentation (confidence 0.48): The training README provides an overview of the optimized Transformer implementation and its speedups, relevant to LRA.
- `flash_attn/cute/flash_fwd_sm120.py` — component (confidence 0.48): This file is part of the FlashAttention implementation for forward pass, which would be used in LRA benchmarks.
- `flash_attn/flash_attn_interface.py` — component (confidence 0.47): This file defines the core FlashAttention function, including variable-length attention, which is relevant for long-range sequences.

**Missing for this claim:**
- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[medium] data_preprocessing** — The paper mentions using the GPT-2 BPE tokenizer for OpenWebText and repeating positional embeddings for long documents. However, it does not detail the specific preprocessing steps for other datasets like MIMIC-III, ECtHR, or the LRA benchmark tasks, nor does it specify any tokenization or normalization procedures beyond the standard ones implied by the model architectures.

**Blockers:**
- Specific LRA benchmark tasks and datasets used
- Code for running LRA benchmarks with FlashAttention
- Code for running LRA benchmarks with baselines for comparison
- Detailed configurations for models used in LRA

**Notes:** While FlashAttention is designed for long sequences, there's no explicit code or configuration in the provided files that directly points to reproducing the LRA benchmark results. The `benchmarks/` directory contains general attention benchmarks, but not LRA specifically.

### Claim 4

> FlashAttention improves perplexity on GPT-2 by 0.7.

**Metric:** perplexity · delta -0.7
**Dataset:** GPT-2
**Method:** FlashAttention vs **Baseline:** ?
**Feasibility:** `medium`

**Evidence:**
> FlashAttention and block-sparse FlashAttention enable longer context in Transformers, yielding higher quality models (0.7 better perplexity on GPT-2 and 6.4 points of lift on long-document classification) and entirely new capabilities: the first Transformers to achieve better-than-chance performance on the Path-X challenge (seq. length 16K, 61.4% accuracy) and Path-256 (seq. length 64K, 63.1% accuracy). _(Page 1)_
> Table 4 shows that that GPT-2 with FlashAttention and context length 4K is still 30% faster than GPT-2 from Megatron with context length 1K, while achieving 0.7 better perplexity. _(Page 8)_

**Code links:**
- `training/README.md` — documentation (confidence 0.64): The training README discusses speedups for GPT models and mentions training scripts, which would be used to evaluate perplexity.
- `README.md` — documentation (confidence 0.58): The main README mentions training scripts for GPT2 on Openwebtext, which is the context for GPT-2 perplexity.
- `flash_attn/cute/README.md` — documentation (confidence 0.56): This README describes FlashAttention-4, which is an optimized version of FlashAttention, relevant for performance and potentially perplexity.
- `README.md` — documentation (confidence 0.55): This section of the README explicitly mentions training GPT2 on Openwebtext, which is the dataset for GPT-2 perplexity evaluation.
- `benchmarks/benchmark_attn.py` — eval script (confidence 0.54): This file contains attention benchmarks, which might include components for evaluating model performance metrics like perplexity, though not directly.
- `flash_attn/models/gpt.py` — model definition (confidence 0.53): This file defines the GPTLMHeadModel, which is the model architecture used for GPT-2 and would be used for perplexity evaluation.

**Missing for this claim:**
- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[medium] data_preprocessing** — The paper mentions using the GPT-2 BPE tokenizer for OpenWebText and repeating positional embeddings for long documents. However, it does not detail the specific preprocessing steps for other datasets like MIMIC-III, ECtHR, or the LRA benchmark tasks, nor does it specify any tokenization or normalization procedures beyond the standard ones implied by the model architectures.

**Blockers:**
- Specific evaluation script for GPT-2 perplexity
- Exact GPT-2 model configuration (e.g., small, medium, large)
- Details on how the baseline perplexity was obtained
- OpenWebText dataset loader and preprocessing for evaluation

**Notes:** The `flash_attn/models/gpt.py` defines the GPT model, and the `training/` directory likely contains the training and evaluation logic. However, a clear, standalone script to reproduce the perplexity claim with specific configurations is not immediately apparent.

### Claim 5

> FlashAttention achieves 61.4% accuracy on the Path-X challenge.

**Metric:** accuracy · proposed 61.4
**Dataset:** Path-X
**Method:** FlashAttention vs **Baseline:** chance
**Feasibility:** `low`

**Evidence:**
> FlashAttention enables the first Transformer that can achieve better-than-chance performance on the Path-X [80] challenge, solely from using a longer sequence length (16K). _(Page 2)_
> FlashAttention achieves 61.4 accuracy on Path-X. _(Page 9)_

**Code links:**
- `README.md` — documentation (confidence 0.60): The main README introduces FlashAttention and its applications, which could include challenges like Path-X.
- `flash_attn/cute/README.md` — documentation (confidence 0.48): This README describes FlashAttention-4, an optimized version, which would be used for performance on various tasks including Path-X.
- `flash_attn/cute/flash_fwd.py` — component (confidence 0.48): This file is part of the FlashAttention forward pass implementation, a core component for any task using FlashAttention.
- `training/README.md` — documentation (confidence 0.47): The training README discusses optimized Transformer implementations, which would be relevant for models tackling Path-X.
- `flash_attn/flash_attn_interface.py` — component (confidence 0.47): This file defines the FlashAttention interface, which would be used in any model employing FlashAttention, including for Path-X.
- `flash_attn/cute/flash_fwd_sm120.py` — component (confidence 0.46): This file is part of the FlashAttention implementation for forward pass, which would be used in Path-X evaluation.

**Missing for this claim:**
- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[medium] data_preprocessing** — The paper mentions using the GPT-2 BPE tokenizer for OpenWebText and repeating positional embeddings for long documents. However, it does not detail the specific preprocessing steps for other datasets like MIMIC-III, ECtHR, or the LRA benchmark tasks, nor does it specify any tokenization or normalization procedures beyond the standard ones implied by the model architectures.

**Blockers:**
- Path-X dataset loader and preprocessing
- Specific model architecture and configuration for Path-X
- Training and evaluation scripts for Path-X
- Definition of 'chance' baseline for accuracy comparison

**Notes:** There is no direct evidence in the repo for Path-X challenge implementation or evaluation. The claim is about accuracy, which implies a specific task and dataset not found in the provided file list.

### Claim 6

> Block-sparse FlashAttention achieves 63.1% accuracy on Path-256.

**Metric:** accuracy · proposed 63.1
**Dataset:** Path-256
**Method:** Block-sparse FlashAttention vs **Baseline:** chance
**Feasibility:** `low`

**Evidence:**
> Block-sparse FlashAttention enables a Transformer to scale to even longer sequences (64K), resulting in the first model that can achieve better-than-chance performance on Path-256. _(Page 2)_
> Additionally, block-sparse FlashAttention enables the Transformers to scale to sequence length 64K, achieving 63.1 accuracy4 on Path-256. _(Page 9)_

**Code links:**
- `README.md` — documentation (confidence 0.63): The main README introduces FlashAttention and its variants, including block-sparse attention, which is relevant to this claim.
- `flash_attn/cute/block_sparse_utils.py` — utility (confidence 0.56): This file contains utilities for block-sparse attention, directly supporting the 'Block-sparse FlashAttention' method.
- `training/README.md` — documentation (confidence 0.54): The training README discusses optimized Transformer implementations, which could include block-sparse variants.
- `flash_attn/cute/flash_fwd_sm120.py` — component (confidence 0.54): This file is part of the FlashAttention forward pass implementation, which could be adapted for block-sparse attention.
- `flash_attn/cute/flash_bwd_sm120.py` — component (confidence 0.54): This file is part of the FlashAttention backward pass implementation, which could be adapted for block-sparse attention.
- `flash_attn/cute/compute_block_sparsity.py` — utility (confidence 0.53): This file is directly related to computing block sparsity, which is central to 'Block-sparse FlashAttention'.

**Missing for this claim:**
- **[high] data_split** — The paper mentions training on the OpenWebText dataset for GPT-2 and Wikipedia for BERT, but does not specify the exact train/validation/test splits used for these datasets. For long-document classification, it mentions MIMIC-III and ECtHR datasets, but the splits are not detailed. For Path-X and Path-256, it mentions pretraining on Path-64 and fine-tuning, but the specific splits for these stages are not provided.
- **[medium] hyperparameters** — While the paper mentions using the LAMB optimizer with learning rate 3.75e-3 for BERT and AdamW with learning rates 6e-4 (GPT-2 small) and 1.5e-4 (GPT-2 medium) for GPT-2, it does not specify the weight decay, beta values for AdamW, or other optimizer-specific hyperparameters. For long-document classification, it states that hyperparameters from Dai et al. [13] are followed, but these are not detailed in the paper. For Path-X and Path-256, it mentions linear warmup and cosine decay of the learning rate, but the specific values for these are not provided.
- **[medium] training_recipe** — The paper mentions using FP16 precision with Apex AMP (O2 optimization level) for BERT training and mixed-precision training (PyTorch AMP) for GPT-2 and LRA benchmarks. However, it does not specify the exact configuration for mixed-precision training (e.g., loss scaling, which operations are cast to FP16/BF16) for all experiments. For LRA, it notes that Performer was not stable with mixed precision and Local Attention did not support FP16, but the specific mixed-precision configurations for other baselines are not detailed.
- **[medium] data_preprocessing** — The paper mentions using the GPT-2 BPE tokenizer for OpenWebText and repeating positional embeddings for long documents. However, it does not detail the specific preprocessing steps for other datasets like MIMIC-III, ECtHR, or the LRA benchmark tasks, nor does it specify any tokenization or normalization procedures beyond the standard ones implied by the model architectures.

**Blockers:**
- Path-256 dataset loader and preprocessing
- Specific model architecture and configuration for Path-256 with block-sparse attention
- Training and evaluation scripts for Path-256
- Definition of 'chance' baseline for accuracy comparison

**Notes:** While the repo contains code for block-sparse attention (`flash_attn/cute/block_sparse_utils.py`, `flash_attn/flash_blocksparse_attention.py`), there's no explicit link to the Path-256 dataset or a script to reproduce this specific accuracy claim.

### Claim 7

> FlashAttention is up to 3x faster than the standard attention implementation across common sequence lengths from 128 to 2K.

**Metric:** runtime speedup · proposed 3.0
**Method:** FlashAttention vs **Baseline:** standard attention implementation
**Feasibility:** `high`

**Evidence:**
> FlashAttention is up to 3× faster than the standard attention implementation across common sequence lengths from 128 to 2K and scales up to 64K. _(Page 2)_
> Runtime grows quadratically with sequence length, but FlashAttention runs significantly faster than exact attention baselines, up to 3× faster than the PyTorch implementation. _(Page 10)_

**Code links:**
- `README.md` — documentation (confidence 0.77): The main README highlights FlashAttention's speed benefits and includes images showing speedup benchmarks, directly relevant to this claim.
- `README.md` — documentation (confidence 0.60): This section of the README discusses overall speedups compared to Huggingface baselines, which implies comparison with standard attention implementations.
- `training/README.md` — documentation (confidence 0.59): The training README discusses speedups and efficiency, which is relevant to runtime speedup comparisons.
- `flash_attn/flash_attn_triton.py` — component (confidence 0.59): This file implements FlashAttention using Triton, which is an alternative implementation that could be used for speed comparisons against standard attention.
- `flash_attn/cute/flash_fwd_sm120.py` — component (confidence 0.58): This file is part of the FlashAttention forward pass implementation, a core component for measuring its speed.
- `flash_attn/flash_attn_interface.py` — component (confidence 0.57): This file defines the core FlashAttention function, which is the primary component whose speed is being measured.

**Notes:** The `benchmarks/` directory contains several benchmark scripts (`benchmark_attn.py`, `benchmark_flash_attention.py`, etc.) that are highly likely to be used for generating these speedup figures. These scripts compare FlashAttention with other implementations, including standard PyTorch attention.

### Claim 8

> FlashAttention is up to 20x more memory efficient than exact attention baselines.

**Metric:** memory efficiency · proposed 20.0
**Method:** FlashAttention vs **Baseline:** exact attention baselines
**Feasibility:** `high`

**Evidence:**
> FlashAttention is up to 20× more memory efficient than exact attention baselines, and is more memory-efficient than the approximate attention baselines. _(Page 10)_

**Code links:**
- `README.md` — documentation (confidence 0.76): The main README mentions FlashAttention's memory efficiency and includes an image related to memory, directly supporting this claim.
- `flash_attn/cute/flash_fwd_sm120.py` — component (confidence 0.58): This file is part of the FlashAttention forward pass implementation, which is designed to be memory efficient.
- `flash_attn/cute/flash_bwd_sm120.py` — component (confidence 0.57): This file is part of the FlashAttention backward pass implementation, also designed for memory efficiency.
- `README.md` — documentation (confidence 0.56): This section of the README mentions not needing activation checkpointing due to efficiency, which is related to memory usage.
- `training/README.md` — documentation (confidence 0.56): The training README discusses optimized Transformer implementations and efficiency, which includes memory efficiency.
- `benchmarks/benchmark_causal.py` — eval script (confidence 0.55): This file contains benchmarks, and memory usage is a common metric evaluated in such benchmarks.

**Notes:** The `benchmarks/` directory likely contains scripts that measure memory usage, similar to how they measure speed. The core FlashAttention implementation is designed with memory efficiency in mind, and the benchmark scripts would be the place to verify this claim.

## Risks

- Lack of explicit, standalone reproduction scripts for specific claims (e.g., BERT MLPerf, LRA, Path-X/256). While benchmark scripts exist, their direct mapping to paper claims is not always clear.
- Dependency on specific hardware (A100 GPUs) and CUDA versions, which might not be universally available.
- Missing detailed hyperparameters and data splits for several experiments, making exact replication challenging.
- Baseline implementations (HuggingFace, Megatron-LM, standard attention) might require specific versions or configurations not fully detailed.

## Next Steps

1. Investigate the `training/` directory for specific GPT-2 and BERT training scripts and their configurations.
2. Examine the `benchmarks/` directory scripts to identify how speedup and memory efficiency are measured and against which baselines.
3. Search for any scripts or documentation related to LRA, Path-X, and Path-256 within the repository.
4. Clarify the exact versions of HuggingFace and Megatron-LM used for baseline comparisons.
5. Identify the specific data splits and preprocessing steps for all datasets mentioned in the claims.
