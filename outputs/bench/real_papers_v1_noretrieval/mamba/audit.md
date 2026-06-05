# Reproducibility Audit

**Paper id:** `2312.00752`
**Benchmark target:** Reproduce the Mamba selective-state-space model on Pile language modeling and recover the perplexity from Table 4.
**Overall feasibility:** `low`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/state-spaces__mamba`
- Important files: README.md, pyproject.toml, setup.py
- Likely entry points: benchmarks/benchmark_generation_mamba_simple.py, evals/lm_harness_eval.py
- Likely eval scripts: evals/lm_harness_eval.py
- Likely config files: mamba_ssm/models/config_mamba.py
- Dependency files: pyproject.toml, setup.py
- Has tests: True
- Notes:
  - uses Hydra configs under configs/
  - no requirements file detected

## Overall Missing Details

- **[medium] random_seed** — The random seeds used for training are not specified. This is crucial for reproducing the exact results, especially for models with stochastic components or initialization.
- **[low] hardware** — While A100 GPUs are mentioned for speed benchmarks, the specific hardware configuration (e.g., number of GPUs, interconnects) used for the main training runs is not detailed. This can impact training time and potentially reproducibility if specific hardware optimizations are assumed.
- **[high] data_split** — While the datasets used (e.g., The Pile, HG38, YouTubeMix, SC09) are mentioned, the exact splits for training, validation, and testing are not provided. This is particularly important for downstream evaluation tasks.
- **[medium] hyperparameters** — While some hyperparameters like learning rate, weight decay, and optimizer are mentioned in the appendix, specific values for all experiments (e.g., for the synthetic tasks, audio generation) are not consistently provided or are described as sweeps without a definitive choice for reproduction. For instance, the learning rate sweep for Mamba in the DNA classification task is mentioned, but the final chosen LR is not explicitly stated for all models.
- **[low] checkpoint** — The paper mentions that code and pre-trained checkpoints are open-sourced, but does not provide direct links or specific details about which checkpoints correspond to which experiments or model sizes. This makes it difficult to directly load and verify specific results.
- **[medium] evaluation_script** — While evaluation metrics are mentioned (e.g., perplexity, accuracy, FID, IS, mIS, AM, NLL, BPB), the exact scripts or configurations used for running these evaluations, especially for downstream tasks, are not provided. The LM-evaluation-harness is mentioned, but specific configurations might be needed.
- **[medium] data_preprocessing** — Details on data preprocessing, such as tokenization specifics (beyond mentioning GPT2 and GPT-NeoX tokenizers), normalization, and any specific cleaning or filtering steps for each modality (language, DNA, audio), are not fully elaborated. For example, the mu-law encoding for audio is mentioned, but the exact parameters or implementation details are missing.
- **[medium] training_recipe** — While some training recipes are described (e.g., AdamW optimizer, learning rate schedules, gradient clipping), specific details for all experiments, especially for the synthetic tasks and audio generation, are not fully specified. The appendix provides more details but might not cover every single experiment.
- **[low] compute_budget** — The total compute budget (e.g., FLOPs, GPU hours) for training the various models, especially the larger language models, is not explicitly stated. While training steps and tokens are mentioned, a consolidated compute budget would aid reproducibility.

## Claims Audit

### Claim 1 — _main claim_

> Mamba-3B model outperforms Transformers of the same size and matches Transformers twice its size on language modeling.

**Method:** Mamba vs **Baseline:** Transformer
**Feasibility:** `medium`

**Evidence:**
> Onlanguagemodeling,ourMamba-3BmodeloutperformsTransformersofthesamesizeandmatchesTransformerstwiceitssize,bothinpretraininganddownstream evaluation.

**Code links:**
- `evals/lm_harness_eval.py` — eval script (confidence 0.80): This script is explicitly named for LM evaluation and likely used to generate perplexity scores for language models like Mamba-3B.
- `mamba_ssm/models/config_mamba.py` — configs (confidence 0.70): This file likely defines the architecture and hyperparameters for different Mamba model sizes, including Mamba-3B.

**Missing for this claim:**
- **[high] data_split** — While The Pile is mentioned, the exact splits for training, validation, and testing are not provided.
- **[medium] training_recipe** — Specific training details for the Mamba-3B model on Pile language modeling, such as total training steps, batch size, and specific learning rate schedule, are not fully specified.
- **[low] checkpoint** — The paper mentions open-sourcing checkpoints but does not provide direct links or specific details for the Mamba-3B model.
- **[medium] random_seed** — The random seeds used for training are not specified. This is crucial for reproducing the exact results, especially for models with stochastic components or initialization.

**Blockers:**
- Lack of specific training script for Mamba-3B on Pile
- Missing exact data splits for The Pile
- Absence of direct checkpoint links for Mamba-3B

**Notes:** Reproducing the 'outperforms Transformers' aspect would also require access to the Transformer models and their training/evaluation setups, which are not part of this repo.

### Claim 2

> Mamba achieves 5x generation throughput compared to Transformers of similar size.

**Metric:** generation throughput · proposed 5.0
**Method:** Mamba vs **Baseline:** Transformer
**Feasibility:** `medium`

**Evidence:**
> OurMambalanguagemodelhas5×generationthroughputcomparedtoTransformersofsimilarsize,andMamba-3B’squalitymatchesthatofTransformerstwiceitssize(e.g.4pointshigheravg.oncommon sensereasoningcomparedtoPythia-3BandevenexceedingPythia-7B).

**Code links:**
- `benchmarks/benchmark_generation_mamba_simple.py` — eval script (confidence 0.90): This script is explicitly designed for benchmarking generation speed of Mamba models, directly relevant to 'generation throughput'.

**Missing for this claim:**
- **[low] hardware** — While A100 GPUs are mentioned for speed benchmarks, the specific hardware configuration (e.g., number of GPUs, interconnects) used for the main training runs is not detailed. This can impact training time and potentially reproducibility if specific hardware optimizations are assumed.
- **[medium] evaluation_script** — The exact configuration or script used for benchmarking the Transformer baseline for comparison is not provided within this repository.

**Blockers:**
- Lack of Transformer baseline benchmarking script/details
- Specific hardware configuration for benchmarking not fully detailed

**Notes:** The `benchmark_generation_mamba_simple.py` script provides a good starting point for Mamba's throughput, but the comparison to Transformers would require external resources or a similar script for Transformers.

### Claim 3

> Mamba generalizes perfectly to million-length sequences on the induction heads task, extrapolating 4000x longer than seen during training.

**Metric:** generalization to million-length sequences · proposed 4000.0
**Dataset:** induction heads
**Method:** Mamba vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> Itgeneralizesperfectlytomillion-lengthsequences,or4000×longerthanitsawduringtraining,whilenoothermethodgoesbeyond2×.

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[high] training_recipe** — The specific training setup, dataset generation, and evaluation script for the induction heads task are not present in the provided repository.
- **[high] data_split** — Details on how the 'million-length sequences' for the induction heads task were generated or split for evaluation are missing.
- **[high] evaluation_script** — A dedicated evaluation script for the induction heads task, especially for extrapolating to 4000x longer sequences, is not found.

**Blockers:**
- Missing dataset generation for induction heads task
- Missing training script for induction heads task
- Missing evaluation script for induction heads task

**Notes:** This claim refers to a synthetic task, and the necessary code for generating the task, training, and evaluating on it is not present in the repo.

### Claim 4

> Mamba is the first attention-free model to match the performance of a strong Transformer recipe (Transformer++) as sequence length grows.

**Dataset:** the Pile
**Method:** Mamba vs **Baseline:** Transformer++
**Feasibility:** `medium`

**Evidence:**
> Mambaisthefirstattention-freemodeltomatchtheperformanceofaverystrongTransformer recipe(Transformer++)thathasnowbecomestandard,particularlyasthesequencelengthgrows.

**Code links:**
- `evals/lm_harness_eval.py` — eval script (confidence 0.80): This script is likely used for evaluating language models on datasets like The Pile, which is relevant for assessing performance as sequence length grows.
- `mamba_ssm/models/config_mamba.py` — configs (confidence 0.70): This file would define the Mamba model architecture used for evaluation on The Pile.

**Missing for this claim:**
- **[high] data_split** — While The Pile is mentioned, the exact splits for training, validation, and testing are not provided, especially for evaluating performance across varying sequence lengths.
- **[medium] training_recipe** — Specific training details for Mamba models on The Pile, particularly how sequence length variations were handled during training or evaluation, are not fully specified.
- **[medium] evaluation_script** — The specific methodology or script for evaluating 'as sequence length grows' and comparing against 'Transformer++' is not detailed or provided.
- **[low] checkpoint** — Checkpoints for the Mamba models evaluated on The Pile are not directly provided.

**Blockers:**
- Missing specific evaluation methodology for varying sequence lengths
- Lack of 'Transformer++' baseline implementation or evaluation details
- Missing exact data splits for The Pile

**Notes:** This claim involves a comparison to 'Transformer++', which is not part of this repository. The evaluation of performance 'as sequence length grows' would require specific evaluation protocols not explicitly detailed.

### Claim 5

> Mamba-1.4B achieves 71.67% accuracy on the Great Apes DNA Classification task at sequence length 1M, outperforming HyenaDNA.

**Metric:** accuracy · proposed 71.67
**Dataset:** Great Apes DNA Classification
**Method:** Mamba vs **Baseline:** HyenaDNA
**Feasibility:** `low`

**Evidence:**
> Mamba 1.4M 31.47 27.50 27.66 40.72 42.41 71.67

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[high] data_preprocessing** — Details on how the Great Apes DNA Classification dataset is loaded, preprocessed, and tokenized for Mamba are missing.
- **[high] training_recipe** — The specific training script and hyperparameters for Mamba-1.4B on the Great Apes DNA Classification task are not provided.
- **[high] evaluation_script** — A dedicated evaluation script for the Great Apes DNA Classification task, including how accuracy is calculated for 1M sequence length, is not present.
- **[high] data_split** — The exact splits for the Great Apes DNA Classification dataset are not provided.

**Blockers:**
- Missing dataset loader and preprocessing for DNA classification
- Missing training script for DNA classification
- Missing evaluation script for DNA classification

**Notes:** This claim refers to a specific downstream task (DNA classification) for which no direct code or configuration is found in the repository.

### Claim 6

> A small Mamba model (6.1M parameters) outperforms state-of-the-art models on the SC09 speech generation dataset with an FID of 0.94.

**Metric:** FID · proposed 0.94
**Dataset:** SC09
**Method:** Mamba vs **Baseline:** SaShiMi
**Feasibility:** `low`

**Evidence:**
> Mamba 6.1M 1.852 0.94 6.26 88.54 0.52

**Code links:**
- (no candidate code links identified)

**Missing for this claim:**
- **[high] data_preprocessing** — Details on how the SC09 speech generation dataset is loaded, preprocessed (e.g., mu-law encoding parameters), and prepared for Mamba are missing.
- **[high] training_recipe** — The specific training script and hyperparameters for the small Mamba model (6.1M parameters) on the SC09 dataset are not provided.
- **[high] evaluation_script** — A dedicated evaluation script for speech generation, including FID calculation, is not present in the repository.
- **[high] data_split** — The exact splits for the SC09 dataset are not provided.

**Blockers:**
- Missing dataset loader and preprocessing for speech generation
- Missing training script for speech generation
- Missing evaluation script for speech generation (FID calculation)

**Notes:** This claim refers to an audio generation task for which no direct code or configuration is found in the repository.

### Claim 7

> Mamba achieves 4-5x higher inference throughput than a Transformer of similar size.

**Metric:** inference throughput · proposed 4.5
**Method:** Mamba vs **Baseline:** Transformer
**Feasibility:** `medium`

**Evidence:**
> Mambaachieves4-5×higherinferencethroughputthanaTransformerofsimilarsize, sincewithouttheKV cache it can use much higher batch sizes.

**Code links:**
- `benchmarks/benchmark_generation_mamba_simple.py` — eval script (confidence 0.90): This script is explicitly designed for benchmarking generation speed of Mamba models, directly relevant to 'inference throughput'.

**Missing for this claim:**
- **[low] hardware** — While A100 GPUs are mentioned for speed benchmarks, the specific hardware configuration (e.g., number of GPUs, interconnects) used for the main training runs is not detailed. This can impact training time and potentially reproducibility if specific hardware optimizations are assumed.
- **[medium] evaluation_script** — The exact configuration or script used for benchmarking the Transformer baseline for comparison is not provided within this repository.

**Blockers:**
- Lack of Transformer baseline benchmarking script/details
- Specific hardware configuration for benchmarking not fully detailed

**Notes:** This claim is very similar to claim 1, focusing on inference throughput. The same `benchmark_generation_mamba_simple.py` script is relevant.

## Risks

- Lack of comprehensive training scripts for specific models and tasks
- Absence of dataset loaders and preprocessing for non-language tasks (DNA, audio)
- Missing evaluation scripts for specialized metrics (FID, induction heads)
- Reliance on external resources for baseline comparisons (Transformers, HyenaDNA, SaShiMi)
- Incomplete hyperparameter details for various experiments

## Next Steps

1. Request full training scripts and configurations for Mamba-3B on The Pile.
2. Request dataset loaders and preprocessing steps for Great Apes DNA Classification and SC09.
3. Request evaluation scripts for induction heads task, DNA classification, and speech generation (FID).
4. Clarify specific hardware setups used for all benchmarks.
5. Obtain direct links to pre-trained checkpoints for all reported models.
