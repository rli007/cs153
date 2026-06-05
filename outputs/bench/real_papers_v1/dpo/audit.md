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
**Feasibility:** `low`

**Evidence:**
> OurexperimentsshowthatDPOcanfine-tunetoLMstoalignwithhumanpreferencesaswellasorbetterthanexistingmethods. _(page 1)_

**Code links:**
- `train.py` — training entry (confidence 0.80): This is the main training script, likely used for DPO fine-tuning.
- `config/loss/dpo.yaml` — configs (confidence 0.90): Configuration file specifically for DPO loss, essential for DPO fine-tuning.
- `trainers.py` — training entry (confidence 0.70): Likely contains the DPO training loop implementation.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.

**Blockers:**
- Missing evaluation scripts and prompts
- Missing full training recipe details
- No model checkpoints provided

**Notes:** This is the main claim, and its reproducibility hinges on the ability to train DPO and evaluate it against baselines, which requires significant missing details.

### Claim 2

> fine-tuning with DPO exceeds PPO-based RLHF in ability to control sentiment of generations.

**Method:** DPO vs **Baseline:** PPO-based RLHF
**Feasibility:** `low`

**Evidence:**
> Notably,fine-tuningwithDPOexceedsPPO-basedRLHFinabilitytocontrolsen-timentofgenerations _(page 1)_

**Code links:**
- `train.py` — training entry (confidence 0.80): Used for DPO training.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.
- `trainers.py` — training entry (confidence 0.70): Likely contains the DPO training loop.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[high] training_recipe** — The paper does not provide the training recipe or code for the PPO-based RLHF baseline, which is crucial for comparison.

**Blockers:**
- Missing PPO baseline implementation/recipe
- Missing evaluation scripts
- No model checkpoints provided

**Notes:** Reproducing this claim requires not only DPO training but also the PPO baseline, which is not provided in the repo.

### Claim 3

> DPO matches or improves response quality in summarization and single-turn dialogue while being substantially simpler to implement and train.

**Method:** DPO vs **Baseline:** existing methods
**Feasibility:** `low`

**Evidence:**
> andmatchesorimprovesresponsequalityinsummarizationandsingle-turndialoguewhilebeingsubstantiallysimplertoimplementandtrain. _(page 1)_

**Code links:**
- `train.py` — training entry (confidence 0.80): General training script for DPO.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[high] training_recipe** — The paper does not provide the training recipe or code for the 'existing methods' baseline, which is crucial for comparison.

**Blockers:**
- Missing baselines for comparison
- Missing evaluation scripts
- No model checkpoints provided

**Notes:** Similar to claim 1, this requires baselines not present in the repo, and also lacks evaluation details.

### Claim 4

> DPO produces by far the most efficient frontier, achieving the highest reward while still achieving low KL.

**Dataset:** IMDb Sentiment Generation
**Method:** DPO vs **Baseline:** PPO
**Feasibility:** `low`

**Evidence:**
> We find that DPO produces by far the most efficient frontier, achieving the highest reward while still achieving low KL. _(page 8)_

**Code links:**
- `train.py` — training entry (confidence 0.80): Used for DPO training on IMDb.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.
- `preference_datasets.py` — dataset loader (confidence 0.70): Likely handles loading of preference datasets, including IMDb.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[high] training_recipe** — The paper does not provide the training recipe or code for the PPO baseline, which is crucial for comparison.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.

**Blockers:**
- Missing PPO baseline implementation/recipe
- Missing evaluation scripts for reward and KL
- No model checkpoints provided
- Missing data split details for IMDb

**Notes:** This claim specifically mentions IMDb and comparison with PPO, requiring both DPO and PPO implementations and detailed evaluation metrics (reward, KL).

### Claim 5

> DPO achieves a better frontier than PPO, even when PPO can access ground truth rewards (PPO-GT).

**Dataset:** IMDb Sentiment Generation
**Method:** DPO vs **Baseline:** PPO-GT
**Feasibility:** `low`

**Evidence:**
> Second,DPOachievesabetterfrontierthanPPO,evenwhenPPOcanaccessgroundtruthrewards(PPO-GT). _(page 8)_

**Code links:**
- `train.py` — training entry (confidence 0.80): Used for DPO training on IMDb.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.
- `preference_datasets.py` — dataset loader (confidence 0.70): Likely handles loading of preference datasets, including IMDb.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[high] training_recipe** — The paper does not provide the training recipe or code for the PPO-GT baseline, which is crucial for comparison.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.

**Blockers:**
- Missing PPO-GT baseline implementation/recipe
- Missing evaluation scripts
- No model checkpoints provided
- Missing data split details for IMDb

**Notes:** Similar to claim 3, but specifically mentions PPO-GT, which is also not provided.

### Claim 6

> DPO has a win rate of approximately 61% at a temperature of 0.0, exceeding the performance of PPO at 57% at its optimal sampling temperature of 0.0.

**Metric:** win rate · proposed 61.0 · delta 4.0
**Dataset:** Reddit TL;DR summarization
**Method:** DPO vs **Baseline:** PPO
**Feasibility:** `low`

**Evidence:**
> WefindthatDPOhasawinrateofapproximately61%ata temperatureof0.0,exceedingtheperformanceofPPOat 57%atitsoptimalsamplingtemperature of 0.0. _(page 9)_

**Code links:**
- `train.py` — training entry (confidence 0.80): Used for DPO training on Reddit TL;DR.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.
- `preference_datasets.py` — dataset loader (confidence 0.70): Likely handles loading of preference datasets, including Reddit TL;DR.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[high] training_recipe** — The paper does not provide the training recipe or code for the PPO baseline, which is crucial for comparison.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.

**Blockers:**
- Missing PPO baseline implementation/recipe
- Missing evaluation scripts for win rate
- No model checkpoints provided
- Missing data split details for Reddit TL;DR

**Notes:** This claim focuses on Reddit TL;DR and win rate, requiring specific evaluation and the PPO baseline.

### Claim 7

> DPO is the only computationally efficient method that improves over the preferred completions in the Anthropic HH dataset.

**Dataset:** Anthropic-HH Dialogue
**Method:** DPO vs **Baseline:** preferred completions
**Feasibility:** `low`

**Evidence:**
> Overall,DPOistheonlycomputationallyefficientmethodthatimprovesoverthepreferredcompletionsintheAnthropic HHdataset _(page 9)_

**Code links:**
- `train.py` — training entry (confidence 0.80): Used for DPO training on Anthropic HH.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.
- `preference_datasets.py` — dataset loader (confidence 0.70): Likely handles loading of preference datasets, including Anthropic HH.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.

**Blockers:**
- Missing evaluation scripts
- No model checkpoints provided
- Missing data split details for Anthropic HH

**Notes:** This claim focuses on Anthropic HH, requiring specific evaluation and data details.

### Claim 8

> DPO continues to outperform the PPO policy by a significant margin on the CNN/DailyMail dataset.

**Dataset:** CNN/DailyMail
**Method:** DPO vs **Baseline:** PPO
**Feasibility:** `low`

**Evidence:**
> Forthisnewdistribution,DPOcontinuestooutperformthePPOpolicybyasignificantmargin. _(page 9)_

**Code links:**
- `train.py` — training entry (confidence 0.80): Used for DPO training on CNN/DailyMail.
- `config/loss/dpo.yaml` — configs (confidence 0.90): DPO specific configuration.
- `preference_datasets.py` — dataset loader (confidence 0.60): Likely handles loading of preference datasets, but CNN/DailyMail is a summarization dataset, not explicitly a preference dataset in the same way as others. Its loading mechanism might be different or require custom handling.

**Missing for this claim:**
- **[medium] evaluation_script** — While the paper describes the evaluation methodology (e.g., using GPT-4 as a proxy for human evaluation, win rates), it does not provide the specific scripts or prompts used for evaluation. The exact prompts for GPT-4 are partially included in Appendix C.2, but the full evaluation pipeline and scoring logic are not detailed.
- **[medium] data_preprocessing** — The paper mentions using datasets like IMDb, Reddit TL;DR, and Anthropic-HH, but does not detail the specific preprocessing steps applied to these datasets before they were used for training or evaluation. This could include tokenization details, handling of special characters, or any filtering applied.
- **[medium] training_recipe** — While the DPO loss function is described and a PyTorch implementation is provided, the full training recipe is not completely specified. This includes details on the number of training epochs or steps, how the reference model is initialized and updated (if applicable), and the exact procedure for sampling from the reference model.
- **[high] checkpoint** — The paper does not provide any information about saving or releasing model checkpoints. To reproduce the results, access to the trained model weights would be necessary.
- **[high] training_recipe** — The paper does not provide the training recipe or code for the PPO baseline, which is crucial for comparison.
- **[medium] data_split** — While the paper mentions using the IMDb dataset for sentiment generation and the Reddit TL;DR dataset for summarization, it does not specify how these datasets were split into training, validation, and testing sets. This information is crucial for reproducing the experiments.

**Blockers:**
- Missing PPO baseline implementation/recipe
- Missing evaluation scripts
- No model checkpoints provided
- Missing data split details for CNN/DailyMail

**Notes:** This claim focuses on CNN/DailyMail, requiring specific evaluation and the PPO baseline.

## Risks

- Lack of baseline implementations (PPO, PPO-GT, other existing methods) makes comparative claims impossible to reproduce.
- Absence of evaluation scripts and prompts means the reported metrics (win rate, reward, KL) cannot be independently verified.
- No model checkpoints are provided, requiring full retraining, which is resource-intensive and sensitive to missing training details.
- Incomplete training recipes and hyperparameter details introduce significant variability in reproduction attempts.
- Data preprocessing and splitting details are missing, which can lead to discrepancies in dataset usage.

## Next Steps

1. Request the authors to provide the code for PPO and other baseline methods used for comparison.
2. Request the authors to release the evaluation scripts, including prompts for GPT-4 and scoring logic.
3. Request the authors to release trained model checkpoints for all reported experiments.
4. Request a comprehensive list of hyperparameters and full training recipes for all experiments.
5. Clarify data preprocessing steps and dataset splits for all datasets used.
