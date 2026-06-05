# Reproducibility Audit

**Paper:** Direct Preference Optimization: Your Language Model is Secretly a Reward Model
**Paper id:** `2305.18290`
**Benchmark target:** Reproduce DPO on the IMDB sentiment task and recover the win-rate vs PPO reported in Section 6.
**Overall feasibility:** `low`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/eric-mitchell__direct-preference-optimization`
- Important files: README.md, requirements.txt, train.py
- Likely entry points: train.py
- Likely eval scripts: none detected
- Likely config files: config/config.yaml, config/loss/dpo.yaml, config/loss/sft.yaml, config/model/blank_model.yaml, config/model/gpt2-large.yaml, config/model/gpt2-xl.yaml, config/model/gptj.yaml, config/model/llama7b.yaml, config/model/pythia28.yaml, config/model/pythia69.yaml
- Dependency files: requirements.txt
- Has tests: False
- Notes:
  - uses Hydra configs under config/
  - no requirements file detected

## Overall Missing Details

- **[medium] random_seed** — The paper mentions using random seeds for preferred-FT in the sentiment experiments, but does not specify the seeds used or if they were used for other experiments. Reproducing the exact results would require knowing the seeds for all experiments.
- **[low] hardware** — The paper mentions using GPU clusters for experiments but does not specify the hardware configuration (e.g., number of GPUs, GPU model, interconnects) used for training the models, which could impact training time and potentially reproducibility if specific hardware optimizations were made.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.
- **[medium] hyperparameters** — While some hyperparameters like beta and batch size are mentioned in Appendix B, the paper does not provide a comprehensive list of all hyperparameters used for training the models across all experiments. For example, learning rate schedules, optimizer parameters (beyond RMSprop), and specific values for other regularization techniques are not fully detailed.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[low] license** — The paper does not mention the license under which the code or models are released. This is important for understanding how the work can be reused and built upon.
- **[low] compute_budget** — The paper mentions training models up to 6B parameters and using GPU clusters, but does not provide specific details on the computational resources (e.g., total GPU hours, number of GPUs used for each experiment) required to reproduce the results. This information is valuable for understanding the feasibility of reproducing the work.

## Claims Audit

### Claim 1 — _main claim_

> DPO can fine-tune LMs to align with human preferences as well as or better than existing methods.

**Method:** DPO vs **Baseline:** existing methods
**Feasibility:** `medium`

**Evidence:**
> OurexperimentsshowthatDPOcanfine-tune LMstoalignwithhumanpreferencesaswellasorbetterthanexistingmethods.

**Code links:**
- `README.md` — training entry (confidence 0.46): The README introduces DPO and its variants, indicating the core algorithm implemented in the repo.
- `config/loss/dpo.yaml` — configs (confidence 0.37): This config file defines parameters specific to the DPO loss function, which is central to the claim.
- `trainers.py` — training entry (confidence 0.25): The `trainers.py` file contains the implementation of the DPO loss calculation, directly supporting the claim about DPO's functionality.
- `config/config.yaml` — configs (confidence 0.20): This general configuration file likely holds global training parameters relevant to DPO fine-tuning.

**Missing for this claim:**
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[medium] hyperparameters** — While some hyperparameters like beta and batch size are mentioned in Appendix B, the paper does not provide a comprehensive list of all hyperparameters used for training the models across all experiments. For example, learning rate schedules, optimizer parameters (beyond RMSprop), and specific values for other regularization techniques are not fully detailed.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.

**Blockers:**
- Missing comprehensive hyperparameters
- Missing full training recipe details
- Missing evaluation scripts and prompts
- No model checkpoints provided

**Notes:** The core DPO implementation is present, but the full experimental setup for fine-tuning and evaluation against 'existing methods' is not fully detailed in the repo or paper.

### Claim 2

> DPO exceeds PPO-based RLHF in ability to control sentiment of generations.

**Method:** DPO vs **Baseline:** PPO-based RLHF
**Feasibility:** `low`

**Evidence:**
> Notably,fine-tuningwithDPOexceedsPPO-basedRLHFinabilitytocontrolsen-timentofgenerations,andmatchesorimprovesresponsequalityinsummarization andsingle-turndialoguewhilebeingsubstantiallysimplertoimplementandtrain.

**Code links:**
- `README.md` — training entry (confidence 0.45): The README introduces DPO, which is the method being compared against PPO.
- `config/loss/dpo.yaml` — configs (confidence 0.38): This config defines the DPO loss parameters, essential for training the DPO model.
- `trainers.py` — training entry (confidence 0.32): Contains the DPO loss calculation and training logic.
- `trainers.py` — eval script (confidence 0.18): The `generate` method in `trainers.py` is used for generating responses, which would be evaluated for sentiment control. This is a component of the evaluation process.

**Missing for this claim:**
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[medium] hyperparameters** — While some hyperparameters like beta and batch size are mentioned in Appendix B, the paper does not provide a comprehensive list of all hyperparameters used for training the models across all experiments. For example, learning rate schedules, optimizer parameters (beyond RMSprop), and specific values for other regularization techniques are not fully detailed.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.
- **[high] training_recipe** — The paper does not provide details on how the PPO baseline was trained or if its implementation is included in the repo, which is crucial for a comparative claim.

**Blockers:**
- Missing PPO baseline implementation or training details
- Missing comprehensive hyperparameters for DPO and PPO
- Missing evaluation scripts for sentiment control
- No model checkpoints provided

**Notes:** The repo focuses on DPO. Reproducing a comparison against PPO would require either the PPO implementation or detailed instructions for its training, which are not present. The evaluation methodology for 'sentiment control' is also not fully specified.

### Claim 3

> DPO matches or improves response quality in summarization and single-turn dialogue compared to PPO-based RLHF.

**Method:** DPO vs **Baseline:** PPO-based RLHF
**Feasibility:** `low`

**Evidence:**
> Notably,fine-tuningwithDPOexceedsPPO-basedRLHFinabilitytocontrolsen-timentofgenerations,andmatchesorimprovesresponsequalityinsummarization andsingle-turndialoguewhilebeingsubstantiallysimplertoimplementandtrain.

**Code links:**
- `README.md` — training entry (confidence 0.30): The README introduces DPO, the method under comparison.
- `preference_datasets.py` — dataset loader (confidence 0.28): This file contains logic for loading preference datasets, including those potentially used for summarization and dialogue (e.g., Anthropic HH).
- `config/loss/dpo.yaml` — configs (confidence 0.25): Defines the DPO loss parameters, central to the DPO training.
- `trainers.py` — training entry (confidence 0.24): Contains the DPO loss calculation and training logic.
- `trainers.py` — eval script (confidence 0.22): The `trainers.py` file includes logic for generating samples during evaluation, which would be used to assess response quality.

**Missing for this claim:**
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[medium] hyperparameters** — While some hyperparameters like beta and batch size are mentioned in Appendix B, the paper does not provide a comprehensive list of all hyperparameters used for training the models across all experiments. For example, learning rate schedules, optimizer parameters (beyond RMSprop), and specific values for other regularization techniques are not fully detailed.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.
- **[high] training_recipe** — The paper does not provide details on how the PPO baseline was trained or if its implementation is included in the repo, which is crucial for a comparative claim.

**Blockers:**
- Missing PPO baseline implementation or training details
- Missing comprehensive hyperparameters for DPO and PPO
- Missing evaluation scripts for response quality (summarization, dialogue)
- No model checkpoints provided

**Notes:** Similar to claim 1, the lack of PPO implementation/details and comprehensive evaluation scripts for summarization and dialogue quality makes this claim difficult to reproduce.

### Claim 4

> DPO has a win rate of approximately 61% at a temperature of 0.0, exceeding the performance of PPO at 57% at its optimal sampling temperature of 0.0 in TL;DR summarization.

**Metric:** win rate · baseline 57.0 · proposed 61.0
**Dataset:** TL;DR Summarization
**Method:** DPO vs **Baseline:** PPO
**Feasibility:** `low`

**Evidence:**
> WefindthatDPOhasawinrateofapproximately61%ata temperatureof0.0,exceedingtheperformanceofPPOat 57%atitsoptimalsamplingtemperature of 0.0.

**Code links:**
- `config/loss/dpo.yaml` — configs (confidence 0.45): This config defines the DPO loss parameters, essential for training the DPO model.
- `README.md` — training entry (confidence 0.43): The README introduces DPO, the method under comparison.
- `trainers.py` — training entry (confidence 0.42): Contains the DPO loss calculation and training logic.
- `trainers.py` — eval script (confidence 0.28): The `trainers.py` file includes logic for generating samples during evaluation, which would be used to assess win rates.

**Missing for this claim:**
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[medium] hyperparameters** — While some hyperparameters like beta and batch size are mentioned in Appendix B, the paper does not provide a comprehensive list of all hyperparameters used for training the models across all experiments. For example, learning rate schedules, optimizer parameters (beyond RMSprop), and specific values for other regularization techniques are not fully detailed.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.
- **[high] training_recipe** — The paper does not provide details on how the PPO baseline was trained or if its implementation is included in the repo, which is crucial for a comparative claim.

**Blockers:**
- Missing PPO baseline implementation or training details
- Missing comprehensive hyperparameters for DPO and PPO
- Missing evaluation scripts for win rate calculation (especially GPT-4 prompts and scoring)
- No model checkpoints provided
- Missing TL;DR dataset split details

**Notes:** This claim is highly specific with numerical results. Reproducing it requires precise details on both DPO and PPO training, the exact TL;DR dataset split, and the full evaluation pipeline, including the GPT-4 prompts and win-rate calculation logic, none of which are fully provided.

### Claim 5

> DPO is the only computationally efficient method that improves over the preferred completions in the Anthropic HH dataset.

**Dataset:** Anthropic HH Dialogue
**Method:** DPO vs **Baseline:** preferred completions
**Feasibility:** `low`

**Evidence:**
> Overall,DPOisthe onlycomputationallyefficientmethodthatimprovesoverthepreferredcompletionsintheAnthropic HHdataset,andprovidessimilarorbetterperformancetothecomputationallydemandingBestof 128baseline.

**Code links:**
- `README.md` — training entry (confidence 0.39): The README introduces DPO, the method central to the claim.
- `config/loss/dpo.yaml` — configs (confidence 0.28): This config defines the DPO loss parameters, essential for training the DPO model.
- `preference_datasets.py` — dataset loader (confidence 0.26): This file explicitly loads the 'Anthropic/hh-rlhf' dataset, which is mentioned in the claim.
- `trainers.py` — training entry (confidence 0.24): Contains the DPO loss calculation and training logic.

**Missing for this claim:**
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[medium] hyperparameters** — While some hyperparameters like beta and batch size are mentioned in Appendix B, the paper does not provide a comprehensive list of all hyperparameters used for training the models across all experiments. For example, learning rate schedules, optimizer parameters (beyond RMSprop), and specific values for other regularization techniques are not fully detailed.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[high] training_recipe** — The claim refers to 'other computationally efficient methods' and 'preferred completions'. The paper does not provide details on how these baselines were established or if their implementations are included in the repo, which is crucial for a comparative claim.

**Blockers:**
- Missing details on 'other computationally efficient methods' and 'preferred completions' baselines
- Missing comprehensive hyperparameters for DPO
- Missing evaluation scripts for comparison on Anthropic HH
- No model checkpoints provided

**Notes:** While the Anthropic HH dataset loader is present, the claim is comparative against unspecified 'other computationally efficient methods' and 'preferred completions'. The methodology for establishing these baselines and the evaluation process for comparison are not detailed.

## Risks

- Lack of comprehensive hyperparameters for all experiments.
- Absence of model checkpoints, requiring full retraining.
- Missing detailed evaluation scripts and prompts, especially for human/GPT-4 evaluations and win-rate calculations.
- Incomplete training recipes, particularly for baselines like PPO.
- Unspecified data splits and preprocessing steps for datasets.

## Next Steps

1. Request comprehensive hyperparameters for all reported experiments (DPO and baselines).
2. Request model checkpoints for DPO and PPO models used in the paper.
3. Request full evaluation scripts, including GPT-4 prompts and win-rate calculation logic.
4. Clarify the exact data splits and preprocessing steps for IMDb, TL;DR, and Anthropic-HH datasets.
5. Seek details on the implementation and training of PPO and other baseline methods for comparative claims.
