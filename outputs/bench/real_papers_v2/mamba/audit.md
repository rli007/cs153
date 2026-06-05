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

- **[high] data_split** — The paper mentions downstream evaluations on various tasks, but the specific data splits (e.g., train/validation/test sets) used for these evaluations are not detailed. This is crucial for reproducing the reported performance metrics.
- **[medium] hyperparameters** — While some hyperparameters like learning rate, weight decay, and optimizer are mentioned (e.g., AdamW with beta values, gradient clipping), specific values for all hyperparameters used in the various experiments (e.g., for synthetic tasks, audio, genomics) are not consistently provided. For instance, the exact learning rate schedule, warmup steps, and decay strategy for all experiments are not fully specified.
- **[medium] training_recipe** — The paper describes general training recipes (e.g., AdamW optimizer, cosine decay, linear warmup) but lacks specific details for all experiments. For example, the exact number of training steps or epochs for each specific task (e.g., audio generation, DNA classification) is not always clear, making it difficult to replicate the training process precisely.
- **[low] compute_budget** — While the paper discusses computational efficiency and provides benchmarks for speed and memory, the exact compute budget (e.g., total FLOPs, GPU hours) for training the largest models or for specific experiments is not explicitly stated. This would be helpful for understanding the scale of computation required for reproduction.
- **[low] other** — The paper mentions using a GPT2 tokenizer for language modeling experiments. However, the specific version or implementation of the GPT2 tokenizer used is not specified, which could lead to minor variations in tokenization and subsequent results.
- **[low] other** — The paper mentions using the AdamW optimizer with specific beta values (0.9, 0.95) and gradient clipping (1.0) for language modeling. However, for other experiments like DNA modeling or audio pretraining, while AdamW is mentioned, the specific beta values and gradient clipping values are not always explicitly stated, leading to potential ambiguity.
- **[low] hardware** — The paper mentions using A100 GPUs for benchmarks and discusses hardware-aware algorithms. However, the specific GPU models and configurations used for the main training experiments are not detailed, which could be relevant for understanding performance and potential reproduction challenges.

## Claims Audit

### Claim 1 — _main claim_

> Mamba-3B model outperforms Transformers of the same size and matches Transformers twice its size, both in pretraining and downstream evaluation.

**Method:** Mamba-3B vs **Baseline:** Transformer
**Feasibility:** `medium`

**Evidence:**
> Onlanguagemodeling,ourMamba-3BmodeloutperformsTransformersofthesamesizeandmatchesTransformerstwiceitssize,bothinpretraininganddownstream evaluation.

**Code links:**
- `evals/lm_harness_eval.py` — eval script (confidence 0.90): This script uses `lm_eval` to evaluate Mamba models, specifically mentioning `mamba-2.8b` and `AutoModelForCausalLM` from Hugging Face, which is relevant for comparing Mamba to Transformers on language modeling tasks.
- `mamba_ssm/models/config_mamba.py` — config (confidence 0.80): Defines the configuration for Mamba models, including `d_model`, `n_layer`, and `vocab_size`, which are crucial for defining model size and architecture for comparison.
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.70): This file defines `MambaLMHeadModel`, a complete language model with Mamba blocks, which would be used for pretraining and subsequent evaluation. The retrieved chunk shows the model's architecture and initialization.
- `README.md` — other (confidence 0.60): The README mentions pretrained models on Hugging Face (e.g., `mamba-130m`, `mamba-370m`) and provides context on how the `mixer_seq_simple.py` is used for end-to-end neural networks, which are likely used for pretraining and evaluation.

**Missing for this claim:**
- **[high] data_split** — The paper mentions downstream evaluations on various tasks, but the specific data splits (e.g., train/validation/test sets) used for these evaluations are not detailed. This is crucial for reproducing the reported performance metrics.
- **[medium] hyperparameters** — While some hyperparameters like learning rate, weight decay, and optimizer are mentioned (e.g., AdamW with beta values, gradient clipping), specific values for all hyperparameters used in the various experiments (e.g., for synthetic tasks, audio, genomics) are not consistently provided. For instance, the exact learning rate schedule, warmup steps, and decay strategy for all experiments are not fully specified.
- **[medium] training_recipe** — The paper describes general training recipes (e.g., AdamW optimizer, cosine decay, linear warmup) but lacks specific details for all experiments. For example, the exact number of training steps or epochs for each specific task (e.g., audio generation, DNA classification) is not always clear, making it difficult to replicate the training process precisely.
- **[medium] other** — The specific Transformer models and their configurations used for comparison are not explicitly detailed, making it hard to ensure a fair comparison.

**Blockers:**
- Missing specific training scripts for pretraining Mamba-3B on Pile.
- Lack of detailed hyperparameters for pretraining and downstream evaluations.
- Absence of specific Transformer model configurations used for comparison.

**Notes:** The `lm_harness_eval.py` script provides a good starting point for evaluation, but the pretraining process to achieve the reported performance is not clearly outlined in the repo.

### Claim 2

> Mamba achieves 5x generation throughput compared to Transformers of similar size.

**Metric:** generation throughput · proposed 5.0
**Method:** Mamba vs **Baseline:** Transformer
**Feasibility:** `medium`

**Evidence:**
> OurMambalanguagemodelhas5×generationthroughputcomparedtoTransformersofsimilarsize,andMamba-3B’squalitymatchesthatofTransformerstwiceitssize(e.g.4pointshigheravg.oncommon sensereasoningcomparedtoPythia-3BandevenexceedingPythia-7B).

**Code links:**
- `benchmarks/benchmark_generation_mamba_simple.py` — eval script (confidence 0.95): This script is explicitly designed for 'Generation benchmarking' and compares Mamba models with `AutoModelForCausalLM` (Transformers), directly addressing the claim of generation throughput comparison.
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.70): This file defines the `MambaLMHeadModel` which is the Mamba architecture used for generation, as imported and used in the benchmark script.
- `README.md` — other (confidence 0.60): The README mentions the `mixer_seq_simple.py` is used in generation scripts, supporting its relevance to generation throughput benchmarks.

**Missing for this claim:**
- **[medium] hyperparameters** — The specific generation parameters (e.g., batch size, sequence length, sampling strategy) used for the throughput benchmark are not fully detailed in the paper or the script, which can significantly impact results.
- **[medium] other** — The exact Transformer models and their configurations used for the throughput comparison are not specified, making it difficult to replicate the 'similar size' comparison accurately.
- **[low] compute_budget** — While the paper discusses computational efficiency and provides benchmarks for speed and memory, the exact compute budget (e.g., total FLOPs, GPU hours) for training the largest models or for specific experiments is not explicitly stated. This would be helpful for understanding the scale of computation required for reproduction.
- **[low] hardware** — The paper mentions using A100 GPUs for benchmarks and discusses hardware-aware algorithms. However, the specific GPU models and configurations used for the main training experiments are not detailed, which could be relevant for understanding performance and potential reproduction challenges.

**Blockers:**
- Lack of explicit generation parameters for the benchmark.
- Unspecified Transformer models for comparison.

**Notes:** The `benchmark_generation_mamba_simple.py` script is a direct entry point for this claim. However, the exact setup for the comparison (e.g., specific Transformer model, generation parameters) needs to be inferred or provided.

### Claim 3

> Mamba generalizes perfectly to million-length sequences, or 4000x longer than its training length, on the induction heads task.

**Metric:** generalization to sequence length · proposed 4000.0
**Dataset:** induction heads
**Method:** Mamba vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> Itgeneralizesperfectlytomillion-lengthsequences,or4000×longerthanitsawduringtraining,whilenoothermethodgoesbeyond2×.

**Code links:**
- `mamba_ssm/utils/generation.py` — eval script (confidence 0.70): This file contains utilities for generation, including handling sequence length and inference parameters, which would be relevant for testing generalization to long sequences. While not a direct 'induction heads task' script, it provides core functionality.
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.60): This defines the Mamba model architecture, which is the subject of the generalization claim.
- `README.md` — other (confidence 0.50): The README mentions the `mixer_seq_simple.py` is used in generation scripts, which are implicitly related to sequence length handling.

**Missing for this claim:**
- **[medium] training_recipe** — The paper describes general training recipes (e.g., AdamW optimizer, cosine decay, linear warmup) but lacks specific details for all experiments. For example, the exact number of training steps or epochs for each specific task (e.g., audio generation, DNA classification) is not always clear, making it difficult to replicate the training process precisely.
- **[high] data_split** — The specific dataset and methodology for the 'induction heads task' are not provided in the repo or paper, making it impossible to reproduce this claim.
- **[medium] hyperparameters** — Specific hyperparameters for training and evaluating on the induction heads task, especially those related to sequence length handling, are missing.

**Blockers:**
- No code or dataset for the 'induction heads task' found.
- Missing specific evaluation script for long sequence generalization.
- Lack of training details for models capable of such generalization.

**Notes:** This claim is highly specific to a particular task ('induction heads') for which no direct code or dataset is provided in the repository. The general generation utilities are not sufficient to reproduce this specific claim.

### Claim 4

> Mamba is the first attention-free model to match the performance of a very strong Transformer recipe (Transformer++) as the sequence length grows.

**Dataset:** the Pile
**Method:** Mamba vs **Baseline:** Transformer++
**Feasibility:** `medium`

**Evidence:**
> Mambaisthefirstattention-freemodeltomatchtheperformanceofaverystrongTransformer recipe(Transformer++)thathasnowbecomestandard,particularlyasthesequencelengthgrows.

**Code links:**
- `evals/lm_harness_eval.py` — eval script (confidence 0.80): This script uses `lm_eval` for language model evaluation, which would be the primary tool for evaluating perplexity on datasets like 'the Pile'.
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.70): This file defines the Mamba language model architecture, which would be trained and evaluated on 'the Pile'.
- `mamba_ssm/models/config_mamba.py` — config (confidence 0.70): Defines the configuration for Mamba models, essential for setting up the model for training and evaluation on 'the Pile'.
- `README.md` — other (confidence 0.60): The README mentions pretrained models and the `mixer_seq_simple.py` for end-to-end language models, which are relevant for this claim.

**Missing for this claim:**
- **[high] data_split** — The paper mentions downstream evaluations on various tasks, but the specific data splits (e.g., train/validation/test sets) used for these evaluations are not detailed. This is crucial for reproducing the reported performance metrics.
- **[medium] hyperparameters** — While some hyperparameters like learning rate, weight decay, and optimizer are mentioned (e.g., AdamW with beta values, gradient clipping), specific values for all hyperparameters used in the various experiments (e.g., for synthetic tasks, audio, genomics) are not consistently provided. For instance, the exact learning rate schedule, warmup steps, and decay strategy for all experiments are not fully specified.
- **[medium] training_recipe** — The paper describes general training recipes (e.g., AdamW optimizer, cosine decay, linear warmup) but lacks specific details for all experiments. For example, the exact number of training steps or epochs for each specific task (e.g., audio generation, DNA classification) is not always clear, making it difficult to replicate the training process precisely.
- **[high] other** — The specific 'Transformer++' recipe and its implementation details are not provided, making a direct comparison difficult.

**Blockers:**
- Missing specific training scripts for Mamba on 'the Pile'.
- Lack of details for the 'Transformer++' baseline.
- Unspecified data splits and hyperparameters for evaluation on 'the Pile'.

**Notes:** While `lm_harness_eval.py` can evaluate perplexity, the full training setup for Mamba on 'the Pile' and the details of the 'Transformer++' baseline are not present in the repo.

### Claim 5

> For each model size, Mamba is best-in-class on every single evaluation result and generally matches baselines at twice the model size.

**Method:** Mamba vs **Baseline:** baselines
**Feasibility:** `low`

**Evidence:**
> Foreachmodelsize,Mambaisbest-in-classoneverysingleevaluationresult,andgenerallymatchesbaselinesattwice themodelsize.

**Code links:**
- `mamba_ssm/models/config_mamba.py` — config (confidence 0.80): This file defines the configurable parameters for Mamba models, allowing for different model sizes (`d_model`, `n_layer`), which is central to the claim about 'each model size'.
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.70): This file implements the Mamba language model, which would be instantiated with different configurations to represent various model sizes.
- `evals/lm_harness_eval.py` — eval script (confidence 0.70): This script is used for evaluating Mamba models, which would be necessary to compare performance across different model sizes and against baselines.
- `README.md` — other (confidence 0.60): The README mentions various pretrained Mamba models of different sizes (e.g., `mamba-130m`, `mamba-370m`), supporting the idea of evaluating different model sizes.

**Missing for this claim:**
- **[high] data_split** — The paper mentions downstream evaluations on various tasks, but the specific data splits (e.g., train/validation/test sets) used for these evaluations are not detailed. This is crucial for reproducing the reported performance metrics.
- **[medium] hyperparameters** — While some hyperparameters like learning rate, weight decay, and optimizer are mentioned (e.g., AdamW with beta values, gradient clipping), specific values for all hyperparameters used in the various experiments (e.g., for synthetic tasks, audio, genomics) are not consistently provided. For instance, the exact learning rate schedule, warmup steps, and decay strategy for all experiments are not fully specified.
- **[medium] training_recipe** — The paper describes general training recipes (e.g., AdamW optimizer, cosine decay, linear warmup) but lacks specific details for all experiments. For example, the exact number of training steps or epochs for each specific task (e.g., audio generation, DNA classification) is not always clear, making it difficult to replicate the training process precisely.
- **[high] other** — The specific 'baselines' and their configurations for comparison are not detailed, making it impossible to reproduce the 'best-in-class' claim.

**Blockers:**
- Lack of specific training and evaluation scripts for various model sizes across 'every single evaluation result'.
- Absence of details for the 'baselines' used for comparison.
- Missing comprehensive evaluation setup for all tasks mentioned in the paper.

**Notes:** This is a very broad claim covering 'every single evaluation result'. The repo provides tools for language model evaluation, but not for all potential tasks implied by 'every single evaluation result'. The baselines are also not specified.

### Claim 6

> Mamba scales better than both HyenaDNA and Transformer++ in DNA pretraining perplexity.

**Dataset:** HG38
**Method:** Mamba vs **Baseline:** HyenaDNA, Transformer++
**Feasibility:** `low`

**Evidence:**
> Figure5(Left)showsthatMamba’spretrainingperplexityimprovessmoothlywithmodelsize,andthatMamba scalesbetterthanbothHyenaDNAandTransformer++.

**Code links:**
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.60): This file defines the Mamba model architecture, which would be adapted for DNA pretraining.
- `mamba_ssm/models/config_mamba.py` — config (confidence 0.60): Defines the configuration for Mamba models, which would be used for DNA pretraining.
- `README.md` — other (confidence 0.50): The README mentions the general Mamba model structure, but no specific DNA-related training or evaluation scripts are present.

**Missing for this claim:**
- **[high] data_split** — The specific data splits for the HG38 dataset used for DNA pretraining are not detailed.
- **[high] training_recipe** — There are no specific training scripts or configurations for DNA pretraining on the HG38 dataset. The general training recipes are insufficient for this specialized task.
- **[medium] hyperparameters** — Specific hyperparameters for DNA pretraining, including learning rates, optimizers, and sequence lengths, are not provided.
- **[high] other** — The implementations or configurations for 'HyenaDNA' and 'Transformer++' for DNA pretraining are not available in the repository.

**Blockers:**
- No specific code for DNA pretraining or evaluation on HG38.
- Missing implementations/configurations for HyenaDNA and Transformer++ baselines.
- Lack of dataset loading and preprocessing for HG38.

**Notes:** The repository focuses on language modeling. There are no explicit files or instructions for DNA pretraining or evaluation, making this claim very difficult to reproduce.

### Claim 7

> Mamba is able to make use of longer context even up to extremely long sequences of length 1M, and its pretraining perplexity improves as the context increases.

**Metric:** pretraining perplexity · proposed 1000000.0
**Dataset:** DNA
**Method:** Mamba vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> Figure5(Right)showsthatMambaisabletomakeuseoflongercontextevenuptoextremelylong sequencesoflength1M,anditspretrainingperplexityimprovesasthecontextincreases.

**Code links:**
- `mamba_ssm/ops/tilelang/mamba3/mamba3_mimo_fwd_varlen.py` — other (confidence 0.70): This file implements variable-length sequence support for Mamba3, which is crucial for handling extremely long sequences up to 1M. While not a direct evaluation script, it shows the architectural capability.
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.60): This defines the Mamba model architecture, which would be used for pretraining with long contexts.
- `README.md` — other (confidence 0.50): The README mentions the general Mamba model structure, but no specific DNA-related training or evaluation scripts are present.

**Missing for this claim:**
- **[high] data_split** — The specific DNA dataset and its splits used for pretraining with 1M length sequences are not detailed.
- **[high] training_recipe** — There are no specific training scripts or configurations for DNA pretraining with extremely long sequences (1M length).
- **[medium] hyperparameters** — Specific hyperparameters for pretraining with 1M length sequences, especially those related to sequence length handling and memory management, are missing.
- **[medium] other** — The methodology for measuring 'pretraining perplexity improves as the context increases' for such long sequences is not detailed.

**Blockers:**
- No specific code for DNA pretraining with 1M length sequences.
- Lack of dataset loading and preprocessing for such long DNA sequences.
- Missing evaluation methodology for perplexity improvement with context.

**Notes:** Similar to claim 5, this claim pertains to DNA modeling with extremely long sequences, for which the repository lacks specific training and evaluation code. While the `varlen` implementations show architectural support, the full experimental setup is missing.

### Claim 8

> A small Mamba model outperforms the state-of-the-art (and much larger) GAN- and diffusion-based models on SC09 speech generation.

**Metric:** FID · proposed 0.94
**Dataset:** SC09
**Method:** Mamba vs **Baseline:** GAN- and diffusion-based models
**Feasibility:** `low`

**Evidence:**
> A small Mambamodel outperformsthestate-of-the-art(andmuchlarger)GAN- anddiffusion-basedmodels.
> Mamba 6.1M 1.852 0.94 6.26 88.54 0.52

**Code links:**
- `mamba_ssm/models/mixer_seq_simple.py` — training entry (confidence 0.60): This file defines the Mamba model architecture, which would be adapted for speech generation.
- `mamba_ssm/models/config_mamba.py` — config (confidence 0.60): Defines the configuration for Mamba models, which would be used for speech generation.
- `README.md` — other (confidence 0.50): The README mentions the general Mamba model structure, but no specific audio-related training or evaluation scripts are present.

**Missing for this claim:**
- **[high] data_split** — The specific data splits for the SC09 speech generation dataset are not detailed.
- **[high] training_recipe** — There are no specific training scripts or configurations for speech generation on the SC09 dataset.
- **[medium] hyperparameters** — Specific hyperparameters for speech generation, including model size, learning rates, and audio processing details, are not provided.
- **[high] other** — The methodology for evaluating FID on SC09 speech generation is not detailed, nor are the implementations of GAN- and diffusion-based models for comparison.

**Blockers:**
- No specific code for SC09 speech generation or evaluation.
- Lack of dataset loading and preprocessing for SC09.
- Missing evaluation methodology for FID and baseline implementations.

**Notes:** The repository is primarily focused on language modeling. There are no explicit files or instructions for speech generation or evaluation on the SC09 dataset, making this claim very difficult to reproduce.

## Risks

- Lack of comprehensive training scripts for various tasks (DNA, audio, specific language modeling pretraining).
- Absence of detailed dataset loaders and preprocessing steps for non-language modeling tasks.
- Missing specific configurations and implementations for baseline models (e.g., Transformer++, HyenaDNA, GANs, diffusion models) for fair comparison.
- Incomplete hyperparameter details for many experiments.
- Reliance on external `lm_eval` harness without full context of its configuration for specific claims.

## Next Steps

1. Request full training scripts and hyperparameters for Mamba models on Pile, DNA, and SC09 datasets.
2. Obtain specific configurations and trained weights for all baseline models used in comparisons.
3. Clarify data splits and preprocessing steps for all datasets mentioned.
4. Seek detailed evaluation methodologies for tasks like 'induction heads' and FID for speech generation.
