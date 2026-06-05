# Reproducibility Audit

**Benchmark target:** reproduce the macro F1 improvement on the held-out validation split
**Overall feasibility:** `low`

## Repository

- Path: `/Users/rli7/Desktop/cs153`
- Important files: README.md, pyproject.toml
- Likely entry points: research_copilot/cli.py, research_copilot/__main__.py
- Likely eval scripts: research_copilot/eval/bench.py, research_copilot/eval/rubric.py
- Likely config files: research_copilot/config.py, benchmarks/case_studies.json
- Dependency files: pyproject.toml
- Has tests: False
- Notes:
  - uses Hydra configs under configs/
  - no requirements file detected
  - entry point defined in pyproject.toml as 'research-copilot = "research_copilot.cli:main"'

## Overall Missing Details

- **[high] data_split** — The paper mentions a 'held-out validation split' and an 'official test set' but does not specify how these splits were created or their sizes. This makes it impossible to reproduce the exact data splits used for evaluation.
- **[medium] hyperparameters** — While the optimizer (Adam), number of epochs (5), and batch size (16) are mentioned, key hyperparameters for Adam (e.g., learning rate, beta1, beta2, epsilon, weight decay) are not specified. These are crucial for reproducing the training process and results.
- **[high] checkpoint** — The model card explicitly states that checkpoint details are not included, and the paper does not provide any information about where to obtain a trained model checkpoint. This prevents direct reproduction of the reported results.
- **[low] hardware** — The model card explicitly states that hardware details are not included. Knowing the hardware used (e.g., GPU type, number of GPUs) can be important for understanding training time and potential performance differences, especially for 'lightweight' models.
- **[medium] training_recipe** — Beyond the optimizer, epochs, and batch size, other aspects of the training recipe such as learning rate scheduling, gradient clipping, regularization techniques, or specific loss function details are not provided. This makes it difficult to fully replicate the training process.
- **[medium] data_preprocessing** — The paper does not describe any data preprocessing steps applied to the technical documents before feeding them into the classifier or retrieval system. This includes details like tokenization, text cleaning, or feature extraction methods.
- **[high] evaluation_script** — The paper reports macro F1 scores but does not provide the evaluation script or specify the exact implementation used to calculate these metrics. This is particularly important for understanding how the 'macro F1' was computed, especially in the context of a multi-class classification task.
- **[medium] random_seed** — No random seeds are mentioned for the training process or data splitting. This is essential for reproducibility, as different random seeds can lead to variations in model performance.

## Claims Audit

### Claim 1 — _main claim_

> On the held-out validation split, the method improves macro F1 from 71.2 to 78.4 compared with a sparse baseline.

**Metric:** macro F1 · baseline 71.2 · proposed 78.4 · delta 7.2
**Dataset:** held-out validation split
**Method:** lightweight retrieval-augmented classifier vs **Baseline:** sparse baseline
**Feasibility:** `low`

**Evidence:**
> On the held-out validation split, the method improves macro F1 from 71.2 to 78.4 compared with a sparse baseline.

**Code links:**
- `research_copilot/eval/bench.py` — eval script (confidence 0.70): This file is identified as a likely evaluation script and would be responsible for calculating metrics like macro F1.
- `research_copilot/eval/rubric.py` — eval script (confidence 0.60): This file appears to be related to scoring and evaluation against ground truth, which might involve metric calculation.
- `research_copilot/cli.py` — training entry (confidence 0.50): As a likely entry point, this script would orchestrate the training and evaluation process, including calling the evaluation script.
- `research_copilot/__main__.py` — training entry (confidence 0.50): As a likely entry point, this script would orchestrate the training and evaluation process, including calling the evaluation script.
- `research_copilot/config.py` — configs (confidence 0.40): Configuration files often specify evaluation parameters or model hyperparameters that influence results.

**Missing for this claim:**
- **[high] data_split** — The paper mentions a 'held-out validation split' and an 'official test set' but does not specify how these splits were created or their sizes. This makes it impossible to reproduce the exact data splits used for evaluation.
- **[medium] hyperparameters** — While the optimizer (Adam), number of epochs (5), and batch size (16) are mentioned, key hyperparameters for Adam (e.g., learning rate, beta1, beta2, epsilon, weight decay) are not specified. These are crucial for reproducing the training process and results.
- **[high] checkpoint** — The model card explicitly states that checkpoint details are not included, and the paper does not provide any information about where to obtain a trained model checkpoint. This prevents direct reproduction of the reported results.
- **[medium] training_recipe** — Beyond the optimizer, epochs, and batch size, other aspects of the training recipe such as learning rate scheduling, gradient clipping, regularization techniques, or specific loss function details are not provided. This makes it difficult to fully replicate the training process.
- **[medium] data_preprocessing** — The paper does not describe any data preprocessing steps applied to the technical documents before feeding them into the classifier or retrieval system. This includes details like tokenization, text cleaning, or feature extraction methods.
- **[high] evaluation_script** — The paper reports macro F1 scores but does not provide the evaluation script or specify the exact implementation used to calculate these metrics. This is particularly important for understanding how the 'macro F1' was computed, especially in the context of a multi-class classification task.
- **[medium] random_seed** — No random seeds are mentioned for the training process or data splitting. This is essential for reproducibility, as different random seeds can lead to variations in model performance.

**Blockers:**
- Missing data split details
- Missing model checkpoint
- Missing evaluation script details
- Incomplete training hyperparameters

## Risks

- Lack of specific data splitting methodology makes it impossible to ensure the same validation set is used.
- Absence of a trained model checkpoint means the model must be re-trained from scratch, introducing variability.
- Incomplete training details (hyperparameters, full recipe) make re-training challenging and potentially lead to different performance.
- The exact calculation of 'macro F1' is not specified, which can lead to discrepancies in evaluation results.

## Next Steps

1. Request the exact data splitting script or methodology used to create the 'held-out validation split'.
2. Request the trained model checkpoint or a detailed guide on how to train the 'lightweight retrieval-augmented classifier' to achieve the reported performance.
3. Obtain the full set of hyperparameters for the Adam optimizer and any other relevant training configurations (e.g., learning rate schedule, regularization).
4. Request the specific evaluation script or a precise definition of how macro F1 was calculated.
