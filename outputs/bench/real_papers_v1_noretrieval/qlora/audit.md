# Reproducibility Audit

**Paper id:** `2305.14314`
**Benchmark target:** Reproduce QLoRA fine-tuning of LLaMA-7B on Alpaca and recover the MMLU score from Table 6.
**Overall feasibility:** `medium`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/artidoro__qlora`
- Important files: README.md, requirements.txt
- Likely entry points: qlora.py, examples/guanaco_generate.py
- Likely eval scripts: eval/eval_gpt_review.py, eval/qa_baseline_gpt.py
- Likely config files: none detected
- Dependency files: eval/requirements.txt, requirements.txt
- Has tests: False
- Notes:
  - uses Hydra configs under configs/
  - no requirements file detected

## Overall Missing Details

- **[medium] training_recipe** — The paper mentions that for OASST1 and HH-RLHF datasets, multiple responses are available and the top response is selected. However, it does not specify how the top response is determined or if any filtering or selection criteria are applied beyond simply picking the 'top' one.
- **[medium] training_recipe** — The paper states that for datasets with a clear distinction between instruction and response, they fine-tune only on the response. However, it does not specify if this is always the case or if there are exceptions, nor does it detail the criteria for distinguishing between instruction and response.
- **[medium] training_recipe** — The paper mentions that for the OASST1 and HH-RLHF datasets, they fine-tune on the full selected conversation, including instructions. However, it does not specify the exact format or structure of these 'full conversations' used for training, which could impact reproducibility.
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[low] hyperparameters** — The paper mentions using Adam beta2 of 0.999 and max grad norm of 0.3. However, the specific value for the Adam beta1 parameter is not provided, which is a standard hyperparameter for the Adam optimizer.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact source length used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact target length used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions that for the OASST1 dataset, they fine-tune on the full conversation including user queries, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the HH-RLHF dataset, they fine-tune on the preferred assistant reply and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the Longform dataset, they fine-tune on the underlying documents and generated instructions, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the Self-Instruct, Alpaca, and Unnatural Instructions datasets, they are instruction tuning datasets collected with various approaches of model distillation. It lists the number of steps in Table 9, but does not specify the exact number of epochs or if early stopping was used for these datasets, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the Chip2 dataset, it contains various types of instructions and examples, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the FLANv2 collection, they use the same task mixtures described by the authors, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 33B model, which is grouped with the 65B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 33B model, which is grouped with the 65B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions using a constant learning rate schedule and group-by-length for batching. However, the specific details of the group-by-length implementation (e.g., how lengths are grouped, tolerance for length differences) are not provided.
- **[medium] hyperparameters** — The paper mentions that for the OASST1 dataset, they fine-tune on the full conversation including user queries, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the HH-RLHF dataset, they fine-tune on the preferred assistant reply and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the Longform dataset, they fine-tune on the underlying documents and generated instructions, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the Self-Instruct, Alpaca, and Unnatural Instructions datasets, they are instruction tuning datasets collected with various approaches of model distillation. It lists the number of steps in Table 9, but does not specify the exact number of epochs or if early stopping was used for these datasets, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the Chip2 dataset, it contains various types of instructions and examples, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[medium] hyperparameters** — The paper mentions that for the FLANv2 collection, they use the same task mixtures described by the authors, and lists the number of steps in Table 9. However, it does not specify the exact number of epochs or if early stopping was used for this specific dataset, which could affect reproducibility.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 33B model, which is grouped with the 65B models.

## Claims Audit

### Claim 1 — _main claim_

> QLoRA reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance.

**Method:** QLoRA vs **Baseline:** 16-bit finetuning
**Feasibility:** `medium`

**Evidence:**
> We present QLORA, an efficient finetuning approach that reduces memory usage enough to finetune a 65B parameter model on a single 48GB GPU while preserving full 16-bit finetuning task performance.

**Code links:**
- `qlora.py` — training entry (confidence 0.80): This file is the main entry point for QLoRA training, likely containing the logic for memory optimization and model finetuning.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Missing specific LoRA alpha value
- Missing exact batch sizes for 65B model
- Missing exact learning rates for 65B model
- Missing exact number of steps for 65B model
- Unclear LoRA dropout for 65B model

### Claim 2

> Our best model family, Guanaco, outperforms all previously openly released models on the Vicuna benchmark, reaching 99.3% of the performance level of ChatGPT.

**Metric:** performance relative to ChatGPT · proposed 99.3
**Dataset:** Vicuna benchmark
**Method:** Guanaco vs **Baseline:** ChatGPT
**Feasibility:** `medium`

**Evidence:**
> Ourbestmodelfamily,whichwenameGuanaco,outperformsallpreviousopenlyreleasedmodelsontheVicunabenchmark, reaching99.3% oftheperformancelevelofChatGPTwhileonlyrequiring24hoursoffinetuningonasingleGPU.

**Code links:**
- `eval/eval_gpt_review.py` — eval script (confidence 0.90): This script is explicitly named for GPT review, which is the methodology described for the Vicuna benchmark evaluation.
- `eval/generations/vicuna/65b-guanaco-vicuna-generations-topp0.9-temp0.7.jsonl` — eval script (confidence 0.70): This file contains pre-generated responses for the Guanaco 65B model on the Vicuna benchmark, which would be used by the evaluation script.
- `eval/prompts/vicuna_prompt_relative.jsonl` — eval script (confidence 0.70): This file likely contains the prompts used for the Vicuna benchmark evaluation, which is crucial for reproducing the results.

**Missing for this claim:**
- **[medium] training_recipe** — The paper mentions that for OASST1 and HH-RLHF datasets, multiple responses are available and the top response is selected. However, it does not specify how the top response is determined or if any filtering or selection criteria are applied beyond simply picking the 'top' one.
- **[medium] training_recipe** — The paper states that for datasets with a clear distinction between instruction and response, they fine-tune only on the response. However, it does not specify if this is always the case or if there are exceptions, nor does it detail the criteria for distinguishing between instruction and response.
- **[medium] training_recipe** — The paper mentions that for the OASST1 and HH-RLHF datasets, they fine-tune on the full selected conversation, including instructions. However, it does not specify the exact format or structure of these 'full conversations' used for training, which could impact reproducibility.
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Lack of full training details for Guanaco models
- Reliance on external GPT-4 API for evaluation

**Notes:** The evaluation script `eval_gpt_review.py` and pre-generated responses for Guanaco on Vicuna are present, suggesting the evaluation process is somewhat reproducible. However, the training details for Guanaco models are not fully specified, and the evaluation relies on an external GPT-4 API, which is a significant blocker for independent reproduction.

### Claim 3

> QLoRA reduces the average memory requirements of finetuning a 65B parameter model from >780GB of GPU memory to <48GB without degrading the runtime or predictive performance compared to a 16-bit fully finetuned baseline.

**Method:** QLoRA vs **Baseline:** 16-bit fully finetuned baseline
**Feasibility:** `medium`

**Evidence:**
> QLORAreducestheaveragememoryrequirements offinetuninga65Bparametermodelfrom>780GB ofGPUmemoryto<48GBwithoutdegradingthe runtimeorpredictiveperformancecomparedtoa16- bitfullyfinetunedbaseline.

**Code links:**
- `qlora.py` — training entry (confidence 0.80): This file is the main entry point for QLoRA training, and would contain the implementation of QLoRA's memory optimization techniques.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Missing specific LoRA alpha value
- Missing exact batch sizes for 65B model
- Missing exact learning rates for 65B model
- Missing exact number of steps for 65B model
- Unclear LoRA dropout for 65B model
- No explicit code for measuring memory usage or runtime comparison against 16-bit baseline

**Notes:** While `qlora.py` implements the core QLoRA method, there's no explicit script or configuration to directly measure and compare memory usage or runtime against a 16-bit baseline as stated in the claim. This would likely require custom instrumentation or external profiling tools.

### Claim 4

> The Guanaco 65B model achieves 99.3% performance relative to ChatGPT on the Vicuna benchmark, trainable in over 24 hours on a single professional GPU.

**Metric:** performance relative to ChatGPT · proposed 99.3
**Dataset:** Vicuna benchmark
**Method:** Guanaco 65B vs **Baseline:** ChatGPT
**Feasibility:** `medium`

**Evidence:**
> using a single professional GPU over 24 hours we achieve 99.3% with our largest model, essentially closing the gap to ChatGPT on the Vicuna bench- mark.

**Code links:**
- `eval/eval_gpt_review.py` — eval script (confidence 0.90): This script is explicitly named for GPT review, which is the methodology described for the Vicuna benchmark evaluation.
- `eval/generations/vicuna/65b-guanaco-vicuna-generations-topp0.9-temp0.7.jsonl` — eval script (confidence 0.70): This file contains pre-generated responses for the Guanaco 65B model on the Vicuna benchmark, which would be used by the evaluation script.
- `eval/prompts/vicuna_prompt_relative.jsonl` — eval script (confidence 0.70): This file likely contains the prompts used for the Vicuna benchmark evaluation, which is crucial for reproducing the results.

**Missing for this claim:**
- **[medium] training_recipe** — The paper mentions that for OASST1 and HH-RLHF datasets, multiple responses are available and the top response is selected. However, it does not specify how the top response is determined or if any filtering or selection criteria are applied beyond simply picking the 'top' one.
- **[medium] training_recipe** — The paper states that for datasets with a clear distinction between instruction and response, they fine-tune only on the response. However, it does not specify if this is always the case or if there are exceptions, nor does it detail the criteria for distinguishing between instruction and response.
- **[medium] training_recipe** — The paper mentions that for the OASST1 and HH-RLHF datasets, they fine-tune on the full selected conversation, including instructions. However, it does not specify the exact format or structure of these 'full conversations' used for training, which could impact reproducibility.
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Lack of full training details for Guanaco 65B model
- Reliance on external GPT-4 API for evaluation
- No explicit code to verify training time on a single professional GPU

**Notes:** Similar to claim 1, the evaluation is present but the training details for Guanaco 65B are not fully specified. Additionally, verifying the '24 hours on a single professional GPU' claim would require specific hardware and detailed logging not explicitly provided.

### Claim 5

> The Guanaco 7B model requires just 5GB of memory and outperforms an Alpaca 13B model by more than 20 percentage points on the Vicuna benchmark.

**Metric:** performance on Vicuna benchmark · delta 20.0
**Dataset:** Vicuna benchmark
**Method:** Guanaco 7B vs **Baseline:** Alpaca 13B
**Feasibility:** `medium`

**Evidence:**
> Whendeployed,oursmallestGuanacomodel (7Bparameters)requiresjust5GBofmemoryandoutperformsa26GBAlpacamodelbymorethan 20percentagepointsontheVicunabenchmark(Table6).

**Code links:**
- `eval/eval_gpt_review.py` — eval script (confidence 0.90): This script is explicitly named for GPT review, which is the methodology described for the Vicuna benchmark evaluation.
- `eval/generations/vicuna/7b-guanaco-vicuna-generations-topp0.9-temp0.7.jsonl` — eval script (confidence 0.70): This file contains pre-generated responses for the Guanaco 7B model on the Vicuna benchmark, which would be used by the evaluation script.
- `eval/generations/vicuna/13b-alpaca-vicuna-generations-topp0.9-temp0.7.jsonl` — eval script (confidence 0.70): This file contains pre-generated responses for the Alpaca 13B model on the Vicuna benchmark, which would be used by the evaluation script for comparison.
- `eval/prompts/vicuna_prompt_relative.jsonl` — eval script (confidence 0.70): This file likely contains the prompts used for the Vicuna benchmark evaluation, which is crucial for reproducing the results.

**Missing for this claim:**
- **[medium] training_recipe** — The paper mentions that for OASST1 and HH-RLHF datasets, multiple responses are available and the top response is selected. However, it does not specify how the top response is determined or if any filtering or selection criteria are applied beyond simply picking the 'top' one.
- **[medium] training_recipe** — The paper states that for datasets with a clear distinction between instruction and response, they fine-tune only on the response. However, it does not specify if this is always the case or if there are exceptions, nor does it detail the criteria for distinguishing between instruction and response.
- **[medium] training_recipe** — The paper mentions that for the OASST1 and HH-RLHF datasets, they fine-tune on the full selected conversation, including instructions. However, it does not specify the exact format or structure of these 'full conversations' used for training, which could impact reproducibility.
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 13B model, which is grouped with the 7B models.

**Blockers:**
- Lack of full training details for Guanaco 7B and Alpaca 13B models
- Reliance on external GPT-4 API for evaluation
- No explicit code to verify memory usage for Guanaco 7B

**Notes:** The evaluation setup for comparing Guanaco 7B and Alpaca 13B on Vicuna is present. However, the training details for both models are not fully specified, and the memory usage claim for Guanaco 7B would need separate verification.

### Claim 6

> NF4 with double quantization fully recovers the 16-bit LoRA MMLU performance on LLaMA 7B-65B models.

**Dataset:** MMLU
**Method:** QLoRA with NF4 + DQ vs **Baseline:** 16-bit LoRA
**Feasibility:** `medium`

**Evidence:**
> We see that NF4 with double quantization fully recovers the 16-bit LoRA MMLU performance.

**Code links:**
- `qlora.py` — training entry (confidence 0.80): This file is the main entry point for QLoRA training and would implement the NF4 and double quantization techniques.
- `data/mmlu/five_shot_mmlu_test.json` — dataset loader (confidence 0.70): This file indicates the presence of MMLU test data, which would be used for evaluation.
- `data/mmlu/five_shot_mmlu_val.json` — dataset loader (confidence 0.70): This file indicates the presence of MMLU validation data, which would be used for evaluation.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 33B model, which is grouped with the 65B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 33B model, which is grouped with the 65B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Missing specific LoRA alpha value
- Missing exact batch sizes for LLaMA models
- Missing exact learning rates for LLaMA models
- Missing exact number of steps for LLaMA models
- Unclear LoRA dropout for LLaMA models
- No explicit MMLU evaluation script found

**Notes:** While `qlora.py` implements the core methods and MMLU data is present, an explicit evaluation script for MMLU is not immediately apparent in the provided file list. The training details for the LLaMA models with different quantization schemes are also not fully specified.

### Claim 7

> QLORA with FP4 lags behind the 16-bit brainfloat LoRA baseline by about 1 percentage point on MMLU.

**Metric:** MMLU performance difference · delta -1.0
**Dataset:** MMLU
**Method:** QLoRA with FP4 vs **Baseline:** 16-bit brainfloat LoRA
**Feasibility:** `medium`

**Evidence:**
> In addition, we also note that QLoRA with FP4 lags behind the 16-bit brainfloat LoRA baseline by about 1 percentage point.

**Code links:**
- `qlora.py` — training entry (confidence 0.80): This file is the main entry point for QLoRA training and would implement the FP4 quantization technique.
- `data/mmlu/five_shot_mmlu_test.json` — dataset loader (confidence 0.70): This file indicates the presence of MMLU test data, which would be used for evaluation.
- `data/mmlu/five_shot_mmlu_val.json` — dataset loader (confidence 0.70): This file indicates the presence of MMLU validation data, which would be used for evaluation.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 33B model, which is grouped with the 65B models.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 7B model, which is grouped with the 13B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 13B model, which is grouped with the 7B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 33B model, which is grouped with the 65B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Missing specific LoRA alpha value
- Missing exact batch sizes for LLaMA models
- Missing exact learning rates for LLaMA models
- Missing exact number of steps for LLaMA models
- Unclear LoRA dropout for LLaMA models
- No explicit MMLU evaluation script found

**Notes:** Similar to claim 5, the core QLoRA implementation is present, and MMLU data is available. However, a dedicated MMLU evaluation script and full training details for the LLaMA models with FP4 quantization are missing.

### Claim 8

> Guanaco 65B achieves 99.3% performance relative to ChatGPT on the Vicuna benchmark, using 4-bit precision and 41GB of memory.

**Metric:** performance relative to ChatGPT · proposed 99.3
**Dataset:** Vicuna benchmark
**Method:** Guanaco 65B vs **Baseline:** ChatGPT
**Feasibility:** `medium`

**Evidence:**
> Guanaco 65B is the best-performing model after GPT-4, achieving 99.3% performance relative to ChatGPT.

**Code links:**
- `eval/eval_gpt_review.py` — eval script (confidence 0.90): This script is explicitly named for GPT review, which is the methodology described for the Vicuna benchmark evaluation.
- `eval/generations/vicuna/65b-guanaco-vicuna-generations-topp0.9-temp0.7.jsonl` — eval script (confidence 0.70): This file contains pre-generated responses for the Guanaco 65B model on the Vicuna benchmark, which would be used by the evaluation script.
- `eval/prompts/vicuna_prompt_relative.jsonl` — eval script (confidence 0.70): This file likely contains the prompts used for the Vicuna benchmark evaluation, which is crucial for reproducing the results.

**Missing for this claim:**
- **[medium] training_recipe** — The paper mentions that for OASST1 and HH-RLHF datasets, multiple responses are available and the top response is selected. However, it does not specify how the top response is determined or if any filtering or selection criteria are applied beyond simply picking the 'top' one.
- **[medium] training_recipe** — The paper states that for datasets with a clear distinction between instruction and response, they fine-tune only on the response. However, it does not specify if this is always the case or if there are exceptions, nor does it detail the criteria for distinguishing between instruction and response.
- **[medium] training_recipe** — The paper mentions that for the OASST1 and HH-RLHF datasets, they fine-tune on the full selected conversation, including instructions. However, it does not specify the exact format or structure of these 'full conversations' used for training, which could impact reproducibility.
- **[medium] hyperparameters** — The paper mentions a hyperparameter search for LoRA over several variables (dropout, r, layers) and that LoRA alpha is kept fixed and learning rate is searched. However, the specific fixed value for LoRA alpha is not provided, which is crucial for reproducing the results.
- **[medium] hyperparameters** — The paper states that LoRA alpha is fixed and learning rate is searched, but the specific fixed value for LoRA alpha is not provided. This is a critical hyperparameter for LoRA.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact batch sizes used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact learning rates used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[medium] hyperparameters** — The paper mentions using a constant learning rate schedule and grouping by length to group examples of similar lengths into the same batch. However, it does not specify the exact number of steps used for each model size and dataset combination, which are listed in Table 9 but not explicitly stated as hyperparameters to be tuned or fixed.
- **[low] hyperparameters** — The paper mentions that LoRA dropout is 0.1 for models up to 13B and 0.05 for 33B and 65B models. However, it does not specify the exact LoRA dropout value used for the 65B model, which is grouped with the 33B models.
- **[low] hyperparameters** — The paper mentions that LoRA modules are added on all linear layers of the base model, and LoRA r is 64 and alpha is 16. However, it does not specify the LoRA dropout value for the 65B model, which is grouped with the 33B models.

**Blockers:**
- Lack of full training details for Guanaco 65B model
- Reliance on external GPT-4 API for evaluation
- No explicit code to verify memory usage for Guanaco 65B

**Notes:** Similar to claims 1 and 3, the evaluation setup is present, but the full training details for Guanaco 65B are not specified. The memory usage claim would also require separate verification.

## Risks

- Reliance on external APIs (GPT-4) for evaluation, which can be costly and introduce variability.
- Incomplete hyperparameter details for training, requiring significant experimentation.
- Lack of explicit evaluation scripts for MMLU, requiring custom implementation.
- Absence of clear instructions or scripts for measuring memory usage and runtime, which are key claims.

## Next Steps

1. Identify the exact configuration files used for training each model variant (e.g., Guanaco 7B, 65B, different quantization schemes).
2. Clarify all missing hyperparameters, especially LoRA alpha, batch sizes, learning rates, and number of steps for each model and dataset.
3. Develop or locate an MMLU evaluation script within the repository or from external sources, ensuring it matches the paper's methodology.
4. Investigate methods to measure GPU memory usage and training runtime to verify the efficiency claims.
5. Address the dependency on the GPT-4 API for Vicuna evaluation, either by finding an alternative or budgeting for API usage.
