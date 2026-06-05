# Reproducibility Audit

**Paper id:** `2106.09685`
**Benchmark target:** Reproduce the LoRA fine-tuning of GPT-2 medium on E2E NLG and recover the published BLEU/ROUGE numbers from Table 2.
**Overall feasibility:** `medium`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/microsoft__LoRA`
- Important files: README.md, setup.py
- Likely entry points: examples/NLU/src/transformers/commands/train.py, examples/NLU/src/transformers/commands/run.py
- Likely eval scripts: none detected
- Likely config files: examples/NLU/ds_config.json
- Dependency files: examples/NLU/environment.yml, examples/NLU/pyproject.toml, examples/NLU/setup.py, setup.py
- Has tests: True
- Notes:
  - uses Hydra configs under configs/
  - no requirements file detected

## Overall Missing Details

- **[medium] random_seed** — The paper mentions reporting the median over 5 random seeds for RoBERTa and DeBERTa, and the mean over 3 random seeds for GPT-2. However, for GPT-3 175B, it states 'we only report the typical standard deviation for a given task over random seeds, as opposed to providing one for every entry.' This implies that specific seeds used for GPT-3 experiments are not disclosed, which could impact reproducibility.
- **[low] hardware** — While the paper mentions using NVIDIA Tesla V100 for all experiments and NVIDIA Quadro RTX 8000 for latency measurements, it does not specify the exact configuration or number of GPUs used for the large-scale GPT-3 175B experiments. This information is crucial for understanding the compute budget and potential for reproduction.
- **[medium] data_split** — The paper refers to using specific datasets (e.g., GLUE, WikiSQL, SAMSum, E2E NLG Challenge, WebNLG, DART) and mentions using training/validation/test splits. However, it does not explicitly detail the exact splits used for each dataset, especially for the validation sets used for reporting results. For instance, for WikiSQL, it states 'contains 56,355/8,421 training/validation examples' but doesn't specify which of the 8,421 are used for validation.
- **[medium] hyperparameters** — While the paper provides hyperparameters in Appendix D for RoBERTa, DeBERTa, GPT-2, and GPT-3, there are some missing details or underspecifications. For example, in Table 9 for RoBERTa, 'LoRAConfig. r =r =8' is mentioned, but it's unclear if this applies to both query (q) and value (v) matrices or if it's a general setting. Similarly, for GPT-3, Table 12 lists 'LearningRate 5.00E-06' for Fine-Tune, but doesn't specify if this is the same for all datasets or if it was tuned per dataset. The paper also mentions sweeping learning rate, number of training epochs, and batch size for LoRA on RoBERTa, but the final chosen values are not always explicitly stated for every task.
- **[medium] training_recipe** — The paper mentions using AdamW optimizer with a linear learning rate decay schedule for most experiments. However, specific details like the exact weight decay values for all models and tasks, or the specific warm-up steps/tokens used for all models (beyond mentioning 250,000 for GPT-3 and 500 for GPT-2) are not consistently provided across all experiments. For instance, Table 10 for DeBERTa lists 'WeightDecay 0 0.01 0.01 0 0.01 0.01 0.01 0.1' which varies by task, but the rationale or tuning process for these specific values is not detailed.
- **[low] other** — The paper mentions releasing a package that facilitates the integration of LoRA with PyTorch models and provides implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at a GitHub repository. However, the specific version of the PyTorch library or other dependencies (e.g., CUDA version, specific versions of libraries like Hugging Face Transformers) are not explicitly stated, which can be critical for reproducing the exact environment.

## Claims Audit

### Claim 1 — _main claim_

> LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times compared to GPT-3 175B fine-tuned with Adam.

**Method:** LoRA vs **Baseline:** GPT-3 175B fine-tuned with Adam
**Feasibility:** `low`

**Evidence:**
> Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times.

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.58): This README explicitly mentions the paper and states that the repo reproduces experiments on GPT-2, which is relevant to the claim about GPT-3 fine-tuning and memory reduction, as it implies the underlying LoRA implementation is present.
- `examples/NLU/README.md` — rationale (confidence 0.59): This README also explicitly mentions the paper and states that the repo contains the implementation of LoRA in RoBERTa and DeBERTa V2, further supporting the presence of the core LoRA implementation.
- `README.md` — rationale (confidence 0.52): The main README introduces the loralib package and mentions its integration with PyTorch models, which is the foundation for the claims about parameter and memory reduction.
- `loralib/layers.py` — training_entry (confidence 0.30): This file likely contains the core LoRA layer implementations (e.g., lora.Linear, lora.MergedLinear) that enable the parameter reduction and thus indirectly the memory reduction. The retrieved chunk shows `lora.Linear` and `lora.MergedLinear`.

**Missing for this claim:**
- **[high] training_recipe** — The specific training script and configuration for GPT-3 175B fine-tuning with Adam, which serves as the baseline for comparison, is not explicitly found in the provided file listing or chunks. The repo focuses on LoRA implementation.
- **[high] training_recipe** — The specific training script and configuration for LoRA fine-tuning of GPT-3 175B, which is the method being evaluated, is not explicitly found in the provided file listing or chunks. The repo provides examples for GPT-2, RoBERTa, and DeBERTa.
- **[medium] hardware** — While the paper mentions using NVIDIA Tesla V100, the exact configuration or number of GPUs used for the large-scale GPT-3 175B experiments is not specified, which is crucial for reproducing memory requirements.

**Blockers:**
- Missing GPT-3 specific training scripts and configurations for both LoRA and baseline Adam fine-tuning.
- Lack of detailed hardware configuration for GPT-3 experiments to verify memory claims.

**Notes:** The repo provides the core `loralib` package and examples for smaller models (GPT-2, RoBERTa, DeBERTa), but direct evidence for reproducing GPT-3 175B experiments is absent. The claim is about GPT-3, which is not directly supported by the provided examples.

### Claim 2

> LoRA performs on-par or better than fine-tuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3.

**Method:** LoRA vs **Baseline:** fine-tuning
**Feasibility:** `medium`

**Evidence:**
> LoRA performs on-par or better than fine-tuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3, despite having fewer trainable parameters, a higher training throughput, and, unlike adapters, no additional inference latency.

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.62): This README explicitly states that the repo reproduces experiments on GPT-2, which is one of the models mentioned in the claim.
- `examples/NLU/README.md` — rationale (confidence 0.57): This README explicitly states that the repo contains the implementation of LoRA in RoBERTa and DeBERTa V2, which are two other models mentioned in the claim.
- `README.md` — rationale (confidence 0.55): The main README introduces the `loralib` package and mentions its integration with PyTorch models, providing the core library for LoRA across various models.
- `examples/NLU/roberta_base_cola.sh` — training_entry (confidence 0.70): These shell scripts (e.g., `roberta_base_cola.sh`, `deberta_v2_xxlarge_cola.sh`) are likely entry points for training LoRA on RoBERTa and DeBERTa models for GLUE tasks, which are mentioned in the claim.
- `examples/NLG/create_datasets.sh` — dataset_loader (confidence 0.60): This script suggests how datasets for NLG tasks (like E2E NLG for GPT-2) might be prepared, which is relevant for reproducing results on GPT-2.

**Missing for this claim:**
- **[high] training_recipe** — While examples for RoBERTa, DeBERTa, and GPT-2 are present, the specific training scripts and configurations for GPT-3 are not provided in the repo. The claim includes GPT-3.
- **[medium] hyperparameters** — The paper mentions sweeping learning rate, number of training epochs, and batch size for LoRA on RoBERTa, but the final chosen values are not always explicitly stated for every task in the provided scripts or documentation.
- **[medium] random_seed** — The paper mentions using multiple random seeds for RoBERTa and DeBERTa, but the specific seeds used are not always explicitly provided in the example scripts.

**Blockers:**
- Missing GPT-3 specific training scripts and configurations.
- Incomplete hyperparameter details for some tasks.
- Specific random seeds not always provided.

**Notes:** The repo provides good coverage for RoBERTa, DeBERTa, and GPT-2, but the inclusion of GPT-3 in the claim makes full reproduction challenging without additional information.

### Claim 3

> LoRA reduces the VRAM usage by up to 2/3 for a large Transformer trained with Adam if r is less than or equal to d.

**Metric:** VRAM usage reduction · proposed 2.0
**Method:** LoRA vs **Baseline:** Adam
**Feasibility:** `low`

**Evidence:**
> For a large Transformer trained with Adam, we reduce that VRAM usage by up to 2/3 if r ⊑ d as we do not need to store the optimizer states for the frozen model parameters.

**Code links:**
- `loralib/layers.py` — training_entry (confidence 0.70): This file contains the core LoRA layer implementations, specifically `lora.Linear` and `lora.MergedLinear`, which are responsible for the low-rank adaptation and thus the parameter reduction that leads to VRAM savings. The chunk shows `self.conv.weight.requires_grad = False`, indicating freezing of pre-trained weights, a key aspect of LoRA's efficiency.
- `examples/NLG/README.md` — rationale (confidence 0.38): This README mentions the paper and the implementation of LoRA in GPT-2, which is a model where VRAM usage reduction would be relevant.
- `examples/NLU/README.md` — rationale (confidence 0.53): This README mentions the paper and the implementation of LoRA in RoBERTa and DeBERTa, also relevant for VRAM usage.

**Missing for this claim:**
- **[high] training_recipe** — The specific scripts or configurations used to measure VRAM usage for both LoRA and baseline Adam fine-tuning are not explicitly provided. While the LoRA implementation is present, the methodology for measuring VRAM reduction is not detailed.
- **[medium] hardware** — The exact hardware configuration and number of GPUs used for VRAM measurements are not fully specified, which is critical for reproducing memory-related claims.

**Blockers:**
- Missing explicit VRAM measurement scripts and methodology.
- Lack of detailed hardware configuration for VRAM measurements.

**Notes:** While the core LoRA implementation is in `loralib/layers.py`, the claim is about a specific metric (VRAM usage reduction) that requires a specific measurement setup not explicitly provided in the repo.

### Claim 4

> LoRA achieves 87.2 average score on GLUE with RoBERTa base, compared to 86.4 for fine-tuning.

**Metric:** Average GLUE score · baseline 86.4 · proposed 87.2 · delta 0.8
**Dataset:** GLUE benchmark
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `medium`

**Evidence:**
> RoB (LoRA) 0.3M 87.5 95.1 89.7 63.4 93.3 90.8 86.6 91.5 87.2
base ±.3 ±.2 ±.7 ±1.2 ±.3 ±.1 ±.7 ±.2
> RoB (FT)* 125.0M 87.6 94.8 90.2 63.6 92.8 91.9 78.7 91.2 86.4
base

**Code links:**
- `examples/NLU/README.md` — rationale (confidence 0.55): This README explicitly mentions 'Adapting to the GLUE Benchmark' for RoBERTa, which is directly relevant to this claim.
- `examples/NLU/roberta_base_cola.sh` — training_entry (confidence 0.80): This script is an example for training RoBERTa base on a GLUE task (CoLA). Similar scripts would be used for other GLUE tasks to achieve the average score.
- `examples/NLU/src/transformers/data/processors/glue.py` — dataset_loader (confidence 0.75): This file likely contains the data processing logic for GLUE benchmark datasets, which is essential for loading and preparing the data for training and evaluation.
- `examples/NLU/src/transformers/commands/train.py` — training_entry (confidence 0.60): This is a general training entry point for transformers models, which would be invoked by the shell scripts for GLUE tasks.
- `examples/NLU/src/transformers/commands/run.py` — eval_script (confidence 0.60): This could be used for running evaluations on trained models, potentially for GLUE tasks.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions sweeping learning rate, number of training epochs, and batch size for LoRA on RoBERTa, but the final chosen values for each specific GLUE task are not always explicitly stated in the provided scripts.
- **[medium] random_seed** — The paper mentions reporting the median over 5 random seeds for RoBERTa, but the specific seeds used for each run are not explicitly provided in the example scripts.
- **[medium] data_split** — The exact validation/test splits used for GLUE tasks are not explicitly detailed, which can affect the reported scores.

**Blockers:**
- Incomplete hyperparameter details for specific GLUE tasks.
- Specific random seeds not provided for all runs.
- Exact data splits not fully detailed.

**Notes:** The repo provides good starting points with shell scripts for RoBERTa on GLUE, but some fine-grained details for exact reproduction are missing.

### Claim 5

> LoRA achieves 89.0 average score on GLUE with RoBERTa large, compared to 88.9 for fine-tuning.

**Metric:** Average GLUE score · baseline 88.9 · proposed 89.0 · delta 0.1
**Dataset:** GLUE benchmark
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `medium`

**Evidence:**
> RoB (FT)* 355.0M 90.2 96.4 90.9 68.0 94.7 92.2 86.6 92.4 88.9
large
> RoB (LoRA) 0.8M 90.6 96.2 90.9 68.2 94.9 91.6 87.4 92.6 89.0
large ±.2 ±.5 ±1.2 ±1.9 ±.3 ±.1 ±2.5 ±.2

**Code links:**
- `examples/NLU/README.md` — rationale (confidence 0.55): This README explicitly mentions 'Adapting to the GLUE Benchmark' for RoBERTa, which is directly relevant to this claim.
- `examples/NLU/roberta_large_cola.sh` — training_entry (confidence 0.80): This script is an example for training RoBERTa large on a GLUE task (CoLA). Similar scripts would be used for other GLUE tasks to achieve the average score.
- `examples/NLU/src/transformers/data/processors/glue.py` — dataset_loader (confidence 0.75): This file likely contains the data processing logic for GLUE benchmark datasets, which is essential for loading and preparing the data for training and evaluation.
- `examples/NLU/src/transformers/commands/train.py` — training_entry (confidence 0.60): This is a general training entry point for transformers models, which would be invoked by the shell scripts for GLUE tasks.
- `examples/NLU/src/transformers/commands/run.py` — eval_script (confidence 0.60): This could be used for running evaluations on trained models, potentially for GLUE tasks.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions sweeping learning rate, number of training epochs, and batch size for LoRA on RoBERTa, but the final chosen values for each specific GLUE task are not always explicitly stated in the provided scripts.
- **[medium] random_seed** — The paper mentions reporting the median over 5 random seeds for RoBERTa, but the specific seeds used for each run are not explicitly provided in the example scripts.
- **[medium] data_split** — The exact validation/test splits used for GLUE tasks are not explicitly detailed, which can affect the reported scores.

**Blockers:**
- Incomplete hyperparameter details for specific GLUE tasks.
- Specific random seeds not provided for all runs.
- Exact data splits not fully detailed.

**Notes:** Similar to claim 3, the repo provides good starting points with shell scripts for RoBERTa large on GLUE, but some fine-grained details for exact reproduction are missing.

### Claim 6

> LoRA achieves 91.3 average score on GLUE with DeBERTa XXL, compared to 91.1 for fine-tuning.

**Metric:** Average GLUE score · baseline 91.1 · proposed 91.3 · delta 0.2
**Dataset:** GLUE benchmark
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `medium`

**Evidence:**
> DeB (FT)* 1500.0M 91.8 97.2 92.0 72.0 96.0 92.7 93.9 92.9 91.1
XXL
> DeB (LoRA) 4.7M 91.9 96.9 92.6 72.4 96.0 92.9 94.9 93.0 91.3
XXL ±.2 ±.2 ±.6 ±1.1 ±.1 ±.1 ±.4 ±.2

**Code links:**
- `examples/NLU/README.md` — rationale (confidence 0.60): This README explicitly mentions 'Adapting to the GLUE Benchmark' for DeBERTa V2, which is directly relevant to this claim.
- `examples/NLU/deberta_v2_xxlarge_cola.sh` — training_entry (confidence 0.80): This script is an example for training DeBERTa XXL on a GLUE task (CoLA). Similar scripts would be used for other GLUE tasks to achieve the average score.
- `examples/NLU/src/transformers/data/processors/glue.py` — dataset_loader (confidence 0.75): This file likely contains the data processing logic for GLUE benchmark datasets, which is essential for loading and preparing the data for training and evaluation.
- `examples/NLU/src/transformers/commands/train.py` — training_entry (confidence 0.60): This is a general training entry point for transformers models, which would be invoked by the shell scripts for GLUE tasks.
- `examples/NLU/src/transformers/commands/run.py` — eval_script (confidence 0.60): This could be used for running evaluations on trained models, potentially for GLUE tasks.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper provides some hyperparameters for DeBERTa in Appendix D, but the final chosen values for each specific GLUE task might not be explicitly stated in the provided scripts.
- **[medium] random_seed** — The paper mentions reporting the median over 5 random seeds for DeBERTa, but the specific seeds used for each run are not explicitly provided in the example scripts.
- **[medium] data_split** — The exact validation/test splits used for GLUE tasks are not explicitly detailed, which can affect the reported scores.

**Blockers:**
- Incomplete hyperparameter details for specific GLUE tasks.
- Specific random seeds not provided for all runs.
- Exact data splits not fully detailed.

**Notes:** The repo provides good starting points with shell scripts for DeBERTa XXL on GLUE, but some fine-grained details for exact reproduction are missing.

### Claim 7

> LoRA achieves 70.4 BLEU on E2E NLG Challenge with GPT-2 medium, outperforming fine-tuning (68.2) and prefix-layer tuning (69.7).

**Metric:** BLEU score · baseline 68.2 · proposed 70.4 · delta 2.2
**Dataset:** E2E NLG Challenge
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `medium`

**Evidence:**
> GPT-2M(FT)* 354.92M 68.2 8.62 46.2 71.0 2.47
> GPT-2M(PreLayer)* 0.35M 69.7 8.81 46.1 71.4 2.49
> GPT-2M(LoRA) 0.35M 70.4 8.85 46.8 71.8 2.53
±.1 ±.02 ±.2 ±.1 ±.02

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.61): This README explicitly states 'Adapting GPT-2 using LoRA' and 'This repo reproduces our experiments on GPT-2', directly supporting the claim about GPT-2 medium on E2E NLG.
- `examples/NLG/README.md` — training_entry (confidence 0.45): The README provides a command-line example for training GPT-2 medium on E2E NLG, including LoRA specific parameters like `--lora_dim` and `--lora_alpha`.
- `examples/NLG/src/gpt2_beam.py` — eval_script (confidence 0.70): The README explicitly mentions using `gpt2_beam.py` to 'Generate outputs from the trained model using beam search', which is necessary for evaluating BLEU scores.
- `examples/NLG/create_datasets.sh` — dataset_loader (confidence 0.60): This script likely handles the preparation of the E2E NLG dataset, which is crucial for the experiment.

**Missing for this claim:**
- **[medium] random_seed** — The paper mentions reporting the mean over 3 random seeds for GPT-2, but the provided example command only specifies one seed (`--random_seed 110`). To reproduce the mean, multiple runs with different seeds are needed.
- **[medium] training_recipe** — The training recipe for the baseline fine-tuning and prefix-layer tuning for GPT-2 medium on E2E NLG is not explicitly provided in the repo, only the LoRA training command.
- **[medium] data_split** — The exact validation/test splits used for the E2E NLG Challenge are not explicitly detailed, which can affect the reported scores.

**Blockers:**
- Only one random seed provided for GPT-2 example, while paper reports mean over 3.
- Missing training recipes for baseline fine-tuning and prefix-layer tuning.
- Exact data splits not fully detailed.

**Notes:** The repo provides a clear training command for LoRA on GPT-2 medium for E2E NLG, making this claim relatively feasible to reproduce for the LoRA part. However, reproducing the baselines and the exact statistical reporting (mean over seeds) requires more information.

### Claim 8

> LoRA achieves 70.4 BLEU on E2E NLG Challenge with GPT-2 large, outperforming fine-tuning (68.5) and prefix-layer tuning (70.3).

**Metric:** BLEU score · baseline 68.5 · proposed 70.4 · delta 1.9
**Dataset:** E2E NLG Challenge
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `medium`

**Evidence:**
> GPT-2L(FT)* 774.03M 68.5 8.78 46.0 69.9 2.45
> GPT-2L(PreLayer)* 0.77M 70.3 8.85 46.2 71.7 2.47
> GPT-2L(LoRA) 0.77M 70.4 8.89 46.8 72.0 2.47
±.1 ±.02 ±.2 ±.02

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.61): This README explicitly states 'Adapting GPT-2 using LoRA' and 'This repo reproduces our experiments on GPT-2', which is relevant to the claim about GPT-2 large on E2E NLG.
- `examples/NLG/README.md` — training_entry (confidence 0.46): The README provides a command-line example for training GPT-2 medium on E2E NLG. While it's for 'medium', the structure would be similar for 'large', implying the necessary components are present.
- `examples/NLG/src/gpt2_beam.py` — eval_script (confidence 0.70): The README explicitly mentions using `gpt2_beam.py` to 'Generate outputs from the trained model using beam search', which is necessary for evaluating BLEU scores for GPT-2 large.
- `examples/NLG/create_datasets.sh` — dataset_loader (confidence 0.60): This script likely handles the preparation of the E2E NLG dataset, which is crucial for the experiment.

**Missing for this claim:**
- **[medium] random_seed** — The paper mentions reporting the mean over 3 random seeds for GPT-2, but the provided example command only specifies one seed (`--random_seed 110`). To reproduce the mean, multiple runs with different seeds are needed.
- **[medium] training_recipe** — The specific training command and configuration for GPT-2 large (as opposed to medium) are not explicitly provided in the README. Also, the training recipes for baseline fine-tuning and prefix-layer tuning for GPT-2 large on E2E NLG are missing.
- **[medium] data_split** — The exact validation/test splits used for the E2E NLG Challenge are not explicitly detailed, which can affect the reported scores.

**Blockers:**
- Only one random seed provided for GPT-2 example, while paper reports mean over 3.
- Missing specific training command for GPT-2 large.
- Missing training recipes for baseline fine-tuning and prefix-layer tuning.
- Exact data splits not fully detailed.

**Notes:** Similar to claim 6, the repo provides a good starting point for GPT-2 NLG, but specific details for the 'large' model and baselines are not explicitly present.

### Claim 9

> On GPT-3 175B, LoRA achieves 73.4 accuracy on WikiSQL with 4.7M parameters, outperforming fine-tuning (73.8) and AdapterH (71.9).

**Metric:** WikiSQL accuracy · baseline 73.8 · proposed 73.4 · delta -0.4
**Dataset:** WikiSQL
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `low`

**Evidence:**
> GPT-3(FT) 175,255.8M 73.8 89.5 52.0/28.0/44.5
> GPT-3(AdapterH) 7.1M 71.9 89.8 53.0/28.9/44.8
> GPT-3(LoRA) 4.7M 73.4 91.7 53.8/29.8/45.9

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.54): This README mentions the paper and the implementation of LoRA in GPT-2, which is a related model, implying the core LoRA functionality is present.
- `examples/NLU/README.md` — rationale (confidence 0.47): This README mentions the paper and the implementation of LoRA in RoBERTa and DeBERTa, also implying the core LoRA functionality is present.
- `README.md` — rationale (confidence 0.44): The main README introduces the `loralib` package, which is the foundation for LoRA implementation.

**Missing for this claim:**
- **[high] training_recipe** — The specific training scripts and configurations for GPT-3 175B on WikiSQL for LoRA, fine-tuning, and AdapterH are not provided in the repo. The repo focuses on GPT-2, RoBERTa, and DeBERTa examples.
- **[medium] data_split** — The exact data splits for WikiSQL are not explicitly detailed, which can affect the reported accuracy.
- **[medium] random_seed** — The paper states that for GPT-3 175B, specific seeds are not disclosed, which impacts reproducibility.

**Blockers:**
- Missing GPT-3 specific training scripts and configurations for all methods.
- Exact data splits not fully detailed.
- Specific random seeds not disclosed for GPT-3.

**Notes:** This claim involves GPT-3 175B, for which no direct examples or configurations are present in the repo. Reproduction would require significant effort to adapt the LoRA library to GPT-3 and implement the baselines.

### Claim 10

> On GPT-3 175B, LoRA achieves 91.7 accuracy on MultiNLI-matched with 4.7M parameters, outperforming fine-tuning (89.5) and AdapterH (89.8).

**Metric:** MultiNLI-matched accuracy · baseline 89.5 · proposed 91.7 · delta 2.2
**Dataset:** MultiNLI-matched
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `low`

**Evidence:**
> GPT-3(FT) 175,255.8M 73.8 89.5 52.0/28.0/44.5
> GPT-3(AdapterH) 7.1M 71.9 89.8 53.0/28.9/44.8
> GPT-3(LoRA) 4.7M 73.4 91.7 53.8/29.8/45.9

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.59): This README mentions the paper and the implementation of LoRA in GPT-2, which is a related model, implying the core LoRA functionality is present.
- `examples/NLU/README.md` — rationale (confidence 0.56): This README mentions the paper and the implementation of LoRA in RoBERTa and DeBERTa, also implying the core LoRA functionality is present.
- `README.md` — rationale (confidence 0.47): The main README introduces the `loralib` package, which is the foundation for LoRA implementation.

**Missing for this claim:**
- **[high] training_recipe** — The specific training scripts and configurations for GPT-3 175B on MultiNLI-matched for LoRA, fine-tuning, and AdapterH are not provided in the repo. The repo focuses on GPT-2, RoBERTa, and DeBERTa examples.
- **[medium] data_split** — The exact data splits for MultiNLI-matched are not explicitly detailed, which can affect the reported accuracy.
- **[medium] random_seed** — The paper states that for GPT-3 175B, specific seeds are not disclosed, which impacts reproducibility.

**Blockers:**
- Missing GPT-3 specific training scripts and configurations for all methods.
- Exact data splits not fully detailed.
- Specific random seeds not disclosed for GPT-3.

**Notes:** This claim involves GPT-3 175B, for which no direct examples or configurations are present in the repo. Reproduction would require significant effort to adapt the LoRA library to GPT-3 and implement the baselines.

### Claim 11

> On GPT-3 175B, LoRA achieves 53.8/29.8/45.9 R1/R2/RL on SAMSum with 4.7M parameters, outperforming fine-tuning (52.0/28.0/44.5) and AdapterH (53.0/28.9/44.8).

**Metric:** SAMSum R1/R2/RL · baseline 52.0 · proposed 53.8 · delta 1.8
**Dataset:** SAMSum
**Method:** LoRA vs **Baseline:** Fine-Tuning(FT)
**Feasibility:** `low`

**Evidence:**
> GPT-3(FT) 175,255.8M 73.8 89.5 52.0/28.0/44.5
> GPT-3(AdapterH) 7.1M 71.9 89.8 53.0/28.9/44.8
> GPT-3(LoRA) 4.7M 73.4 91.7 53.8/29.8/45.9

**Code links:**
- `examples/NLG/README.md` — rationale (confidence 0.63): This README mentions the paper and the implementation of LoRA in GPT-2, which is a related model, implying the core LoRA functionality is present.
- `examples/NLU/README.md` — rationale (confidence 0.52): This README mentions the paper and the implementation of LoRA in RoBERTa and DeBERTa, also implying the core LoRA functionality is present.
- `README.md` — rationale (confidence 0.44): The main README introduces the `loralib` package, which is the foundation for LoRA implementation.

**Missing for this claim:**
- **[high] training_recipe** — The specific training scripts and configurations for GPT-3 175B on SAMSum for LoRA, fine-tuning, and AdapterH are not provided in the repo. The repo focuses on GPT-2, RoBERTa, and DeBERTa examples.
- **[medium] data_split** — The exact data splits for SAMSum are not explicitly detailed, which can affect the reported R1/R2/RL scores.
- **[medium] random_seed** — The paper states that for GPT-3 175B, specific seeds are not disclosed, which impacts reproducibility.

**Blockers:**
- Missing GPT-3 specific training scripts and configurations for all methods.
- Exact data splits not fully detailed.
- Specific random seeds not disclosed for GPT-3.

**Notes:** This claim involves GPT-3 175B, for which no direct examples or configurations are present in the repo. Reproduction would require significant effort to adapt the LoRA library to GPT-3 and implement the baselines.

## Risks

- The repository provides implementations for LoRA on smaller models (GPT-2, RoBERTa, DeBERTa) but lacks direct support or examples for GPT-3 175B, which is central to several claims. Reproducing GPT-3 results would require significant additional effort.
- Consistent reporting of random seeds is missing across all experiments, making it difficult to reproduce exact statistical results (e.g., mean/median over multiple runs).
- Detailed hyperparameters for all tasks and models, especially for baselines (fine-tuning, AdapterH, prefix-layer tuning), are not fully specified in the repo or paper, requiring extensive hyperparameter tuning.
- Exact data splits for validation/test sets are not always explicitly detailed, which can lead to discrepancies in reported metrics.

## Next Steps

1. Investigate if there are any community efforts or external resources that provide GPT-3 175B fine-tuning scripts compatible with the `loralib` package.
2. For claims involving GPT-2, RoBERTa, and DeBERTa, attempt to run the provided example scripts and verify the results. Document any discrepancies and the effort required to match the paper's reported numbers.
3. For claims where multiple random seeds are mentioned, identify if the provided scripts can be easily modified to run multiple times with different seeds and aggregate results.
4. For missing hyperparameters, consult the paper's appendix more thoroughly and try to infer reasonable values or conduct small-scale hyperparameter searches if necessary.
