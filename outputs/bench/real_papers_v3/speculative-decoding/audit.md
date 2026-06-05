# Reproducibility Audit

**Paper id:** `2211.17192`
**Benchmark target:** Reproduce the speculative decoding speedup claim: 2x-3x faster inference than standard autoregressive decoding while preserving the target model output distribution.
**Overall feasibility:** `low`

## Repository

- Path: `/Users/rli7/Desktop/cs153/.cache/repos/romsto__Speculative-Decoding`
- Important files: README.md, requirements.txt
- Likely entry points: infer.py
- Likely eval scripts: none detected
- Likely config files: none detected
- Dependency files: requirements.txt
- Has tests: False
- Notes:
  - No requirements file detected
  - Uses Hydra configs under configs/ (not present in listing)

## Overall Missing Details

- **[high] data_split** — The paper mentions using existing checkpoints for models like T5-XXL, T5-small, T5-base, and T5-large, but it does not specify the exact data splits used for training or fine-tuning these models. This information is crucial for reproducing the exact performance and behavior of the models used as the target and approximation models.
- **[medium] hyperparameters** — While the paper mentions using T5-XXL, T5-small, T5-base, and T5-large models and their existing checkpoints, it does not specify the exact hyperparameters used for fine-tuning these models on the English-German translation (WMTEnDe) and CNN/DM summarization tasks. This includes learning rate, batch size (though batch size of 1 is mentioned for inference), number of epochs, optimizer, etc. The paper does mention using a batch size of 1 for inference.
- **[medium] hyperparameters** — The paper mentions using a GPT-like Transformer decoder with 6M parameters for the approximation model and a 97M parameter model for the target model in the unconditional language generation task. However, the specific hyperparameters for these models (e.g., number of layers, attention heads, hidden dimensions, feed-forward dimensions, activation functions, dropout rates) are not fully detailed, beyond mentioning 'dim256, dim feed-forward 1024, 2 layers, 4 attention heads' for the 6M model and 'dim768, dim feed-forward 3072, 12 layers, 12 attention heads' for the 97M model. The activation function (Gelu) and tokenizer (Bert) are mentioned, but other training hyperparameters are missing.
- **[medium] hyperparameters** — For the LaMDA models (137B, 8B, 2B, 100M), the paper states that existing checkpoints were used. However, specific hyperparameters for these models, especially for the approximation models (8B, 2B, 100M), are not provided, which could affect their performance as approximation models.
- **[low] hyperparameters** — The paper mentions using 'existing checkpoints' for the LaMDA models. It would be beneficial to know if any specific fine-tuning or configuration was applied to these checkpoints before using them as approximation models, especially if they were not originally trained for this specific speculative decoding purpose.
- **[low] hyperparameters** — The paper mentions using 'existing checkpoints' for the T5 models. It would be beneficial to know if any specific fine-tuning or configuration was applied to these checkpoints before using them as approximation models, especially if they were not originally trained for this specific speculative decoding purpose.
- **[medium] data_preprocessing** — The paper mentions using 'Bert tokenization with 8k tokens for all models' for the GPT-like models. However, details about other preprocessing steps, such as text cleaning, normalization, or any specific tokenization strategies beyond the mention of Bert tokenizer and vocabulary size, are not provided. This could impact the exact token sequences generated and thus the performance.
- **[high] training_recipe** — The paper states that 'existing checkpoints' are used for T5 and LaMDA models. However, it does not detail the training recipe (e.g., optimizer, learning rate schedule, regularization) used to obtain these checkpoints, which could influence their behavior as target or approximation models.
- **[high] training_recipe** — For the GPT-like models, while some architectural details are provided, the specific training recipe (e.g., optimizer, learning rate, batch size, training duration, regularization techniques) used to train the 6M and 97M parameter models is not specified. This is crucial for understanding how the approximation and target models were created.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.
- **[medium] compute_budget** — While the paper discusses theoretical speedups and provides empirical results, it does not explicitly state the compute budget (e.g., total FLOPs, training time, inference time) for training the custom GPT-like models or for the experiments involving LaMDA models. This would help in understanding the overall resource requirements.
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 and LaMDA models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] other** — The paper mentions using 'existing checkpoints' for the T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] other** — The paper mentions using 'existing checkpoints' for the LaMDA models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[low] other** — The paper mentions using 'Bert tokenization (Devlin et al., 2019) with 8k tokens for all models' for the GPT-like models. It would be beneficial to specify the exact vocabulary file or provide a link to it, as different versions or implementations of the BERT tokenizer might exist.
- **[medium] other** — The paper mentions that the LaMDA models go through a 'Top filter'. The specifics of this filter (e.g., its parameters, implementation) are not detailed, which could affect the sampling process and thus the reproducibility of results.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.

## Claims Audit

### Claim 1 — _main claim_

> Our method can accelerate existing off-the-shelf models without retraining or architecture changes, demonstrating a 2X-3X acceleration compared to the standard T5X implementation, with identical outputs.

**Method:** speculative decoding vs **Baseline:** T5X
**Feasibility:** `medium`

**Evidence:**
> We demonstrate it on T5-XXL and show a 2X-3X acceleration compared to the standard T5X implementation, with identical outputs.

**Code links:**
- `README.md` — training entry (confidence 0.50): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, including auto-regressive and speculative decoding, which are central to the claim of acceleration.
- `sampling/speculative_decoding.py` — training entry (confidence 0.33): This file likely contains the core implementation of the speculative decoding algorithm, which is the method being evaluated for speedup.
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.36): This file likely contains the core implementation of the speculative decoding algorithm, which is the method being evaluated for speedup, specifically for encoder-decoder models.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and potentially measuring wall times for different decoding strategies.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5X implementation and specific version
- Availability of T5-XXL model checkpoints
- Specific hardware configuration for wall-time measurements

**Notes:** The repository provides the implementation of speculative decoding, but the comparison against T5X and the specific models (T5-XXL) are not directly present in the provided files. The README mentions 'classic auto-regressive decoding' which could be the baseline, but the T5X specific implementation is not clear.

### Claim 2

> We implement our method and compare actual wall times for T5-XXL to those of the robust T5X implementation, showing an out-of-the-box latency improvement of 2X-3X, without any change to the outputs.

**Method:** speculative decoding vs **Baseline:** T5X
**Feasibility:** `medium`

**Evidence:**
> We implement our method and compare actual wall times for T5-XXL to those of the robust T5X implementation, showing an out-of-the-box latency improvement of 2X-3X, without any change to the outputs.

**Code links:**
- `README.md` — training entry (confidence 0.46): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, including auto-regressive and speculative decoding, which are central to the claim of acceleration.
- `sampling/speculative_decoding.py` — training entry (confidence 0.30): This file likely contains the core implementation of the speculative decoding algorithm, which is the method being evaluated for speedup.
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.29): This file likely contains the core implementation of the speculative decoding algorithm, which is the method being evaluated for speedup, specifically for encoder-decoder models.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and measuring wall times for different decoding strategies.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5X implementation and specific version
- Availability of T5-XXL model checkpoints
- Specific hardware configuration for wall-time measurements

**Notes:** Similar to claim 0, the core speculative decoding implementation is present, but the specific T5X baseline and T5-XXL model are not directly provided or referenced in a reproducible manner within the repo.

### Claim 3

> For the English to German translation task, using T5-XXL (11B) as the target model and T5-small (77M) as the approximation model with argmax sampling (temp=0), we achieve a speedup of 3.4X.

**Metric:** speedup · proposed 3.4
**Dataset:** WMTEnDe
**Method:** speculative decoding vs **Baseline:** T5X
**Feasibility:** `low`

**Evidence:**
> We see that T5-small (77M), with a good balance of c and α, provides the highest speedup out of the tested q approximation models. As expected we see that α increases with the size of the approximation model. Interestingly, α and walltime improvement are higher for argmax sampling (temp=0). We observe speedups of 2.6X(temp=1) and 3.4X (temp=0) on the translation task and slightly lower speedups of 2.3X(temp=1) and 3.1X(temp=0) for the summarization task.

**Code links:**
- `README.md` — training entry (confidence 0.46): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, which are central to the claim.
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.38): This file contains the `autoregressive_generate_encoder_decoder` function, which is likely used for T5 models (encoder-decoder architecture) and includes logic for speculative decoding.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and measuring wall times for different decoding strategies, including for T5 models.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] data_split** — The paper mentions using existing checkpoints for models like T5-XXL, T5-small, T5-base, and T5-large, but it does not specify the exact data splits used for training or fine-tuning these models. This information is crucial for reproducing the exact performance and behavior of the models used as the target and approximation models.
- **[medium] hyperparameters** — While the paper mentions using T5-XXL, T5-small, T5-base, and T5-large models and their existing checkpoints, it does not specify the exact hyperparameters used for fine-tuning these models on the English-German translation (WMTEnDe) and CNN/DM summarization tasks. This includes learning rate, batch size (though batch size of 1 is mentioned for inference), number of epochs, optimizer, etc. The paper does mention using a batch size of 1 for inference.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5-XXL and T5-small model checkpoints (especially for WMTEnDe task)
- Specific T5X baseline implementation details
- Dataset (WMTEnDe) loading and preprocessing for T5 models
- Exact hyperparameters for T5 models on the task

**Notes:** The claim relies on specific T5 models and a specific dataset (WMTEnDe). While the code has speculative decoding for encoder-decoder models, the actual models and dataset loading are not present. The README shows an example of loading a tokenizer, but not the full model or dataset for evaluation.

### Claim 4

> For the English to German translation task, using T5-XXL (11B) as the target model and T5-small (77M) as the approximation model with standard sampling (temp=1), we achieve a speedup of 2.6X.

**Metric:** speedup · proposed 2.6
**Dataset:** WMTEnDe
**Method:** speculative decoding vs **Baseline:** T5X
**Feasibility:** `low`

**Evidence:**
> We see that T5-small (77M), with a good balance of c and α, provides the highest speedup out of the tested q approximation models. As expected we see that α increases with the size of the approximation model. Interestingly, α and walltime improvement are higher for argmax sampling (temp=0). We observe speedups of 2.6X(temp=1) and 3.4X (temp=0) on the translation task and slightly lower speedups of 2.3X(temp=1) and 3.1X(temp=0) for the summarization task.

**Code links:**
- `README.md` — training entry (confidence 0.46): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, which are central to the claim.
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.39): This file contains the `autoregressive_generate_encoder_decoder` function, which is likely used for T5 models (encoder-decoder architecture) and includes logic for speculative decoding.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and measuring wall times for different decoding strategies, including for T5 models.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] data_split** — The paper mentions using existing checkpoints for models like T5-XXL, T5-small, T5-base, and T5-large, but it does not specify the exact data splits used for training or fine-tuning these models. This information is crucial for reproducing the exact performance and behavior of the models used as the target and approximation models.
- **[medium] hyperparameters** — While the paper mentions using T5-XXL, T5-small, T5-base, and T5-large models and their existing checkpoints, it does not specify the exact hyperparameters used for fine-tuning these models on the English-German translation (WMTEnDe) and CNN/DM summarization tasks. This includes learning rate, batch size (though batch size of 1 is mentioned for inference), number of epochs, optimizer, etc. The paper does mention using a batch size of 1 for inference.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5-XXL and T5-small model checkpoints (especially for WMTEnDe task)
- Specific T5X baseline implementation details
- Dataset (WMTEnDe) loading and preprocessing for T5 models
- Exact hyperparameters for T5 models on the task

**Notes:** Similar to claim 2, this claim requires specific T5 models and the WMTEnDe dataset, which are not directly provided or configured in the repository for evaluation.

### Claim 5

> For the text summarization task (CNN/DM), using T5-XXL (11B) as the target model and T5-small (77M) as the approximation model with argmax sampling (temp=0), we achieve a speedup of 3.1X.

**Metric:** speedup · proposed 3.1
**Dataset:** CCN/DM
**Method:** speculative decoding vs **Baseline:** T5X
**Feasibility:** `low`

**Evidence:**
> We see that T5-small (77M), with a good balance of c and α, provides the highest speedup out of the tested q approximation models. As expected we see that α increases with the size of the approximation model. Interestingly, α and walltime improvement are higher for argmax sampling (temp=0). We observe speedups of 2.6X(temp=1) and 3.4X (temp=0) on the translation task and slightly lower speedups of 2.3X(temp=1) and 3.1X(temp=0) for the summarization task.

**Code links:**
- `README.md` — training entry (confidence 0.41): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, which are central to the claim.
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.30): This file contains the `autoregressive_generate_encoder_decoder` function, which is likely used for T5 models (encoder-decoder architecture) and includes logic for speculative decoding.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and measuring wall times for different decoding strategies, including for T5 models.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] data_split** — The paper mentions using existing checkpoints for models like T5-XXL, T5-small, T5-base, and T5-large, but it does not specify the exact data splits used for training or fine-tuning these models. This information is crucial for reproducing the exact performance and behavior of the models used as the target and approximation models.
- **[medium] hyperparameters** — While the paper mentions using T5-XXL, T5-small, T5-base, and T5-large models and their existing checkpoints, it does not specify the exact hyperparameters used for fine-tuning these models on the English-German translation (WMTEnDe) and CNN/DM summarization tasks. This includes learning rate, batch size (though batch size of 1 is mentioned for inference), number of epochs, optimizer, etc. The paper does mention using a batch size of 1 for inference.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5-XXL and T5-small model checkpoints (especially for CNN/DM task)
- Specific T5X baseline implementation details
- Dataset (CNN/DM) loading and preprocessing for T5 models
- Exact hyperparameters for T5 models on the task

**Notes:** This claim also relies on specific T5 models and the CNN/DM dataset, which are not directly provided or configured for evaluation in the repository.

### Claim 6

> For the text summarization task (CNN/DM), using T5-XXL (11B) as the target model and T5-small (77M) as the approximation model with standard sampling (temp=1), we achieve a speedup of 2.3X.

**Metric:** speedup · proposed 2.3
**Dataset:** CCN/DM
**Method:** speculative decoding vs **Baseline:** T5X
**Feasibility:** `low`

**Evidence:**
> We see that T5-small (77M), with a good balance of c and α, provides the highest speedup out of the tested q approximation models. As expected we see that α increases with the size of the approximation model. Interestingly, α and walltime improvement are higher for argmax sampling (temp=0). We observe speedups of 2.6X(temp=1) and 3.4X (temp=0) on the translation task and slightly lower speedups of 2.3X(temp=1) and 3.1X(temp=0) for the summarization task.

**Code links:**
- `README.md` — training entry (confidence 0.42): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, which are central to the claim.
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.30): This file contains the `autoregressive_generate_encoder_decoder` function, which is likely used for T5 models (encoder-decoder architecture) and includes logic for speculative decoding.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and measuring wall times for different decoding strategies, including for T5 models.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] data_split** — The paper mentions using existing checkpoints for models like T5-XXL, T5-small, T5-base, and T5-large, but it does not specify the exact data splits used for training or fine-tuning these models. This information is crucial for reproducing the exact performance and behavior of the models used as the target and approximation models.
- **[medium] hyperparameters** — While the paper mentions using T5-XXL, T5-small, T5-base, and T5-large models and their existing checkpoints, it does not specify the exact hyperparameters used for fine-tuning these models on the English-German translation (WMTEnDe) and CNN/DM summarization tasks. This includes learning rate, batch size (though batch size of 1 is mentioned for inference), number of epochs, optimizer, etc. The paper does mention using a batch size of 1 for inference.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5-XXL and T5-small model checkpoints (especially for CNN/DM task)
- Specific T5X baseline implementation details
- Dataset (CNN/DM) loading and preprocessing for T5 models
- Exact hyperparameters for T5 models on the task

**Notes:** Similar to claim 4, this claim requires specific T5 models and the CNN/DM dataset, which are not directly provided or configured for evaluation in the repository.

### Claim 7

> For the English to German translation task, using T5-XXL (11B) as the target model and a trivial bigram model as the approximation model, we get an inference speed improvement factor of 1.25X.

**Metric:** speed improvement factor · proposed 1.25
**Dataset:** WMTEnDe
**Method:** speculative decoding vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> Interestingly, in empirical tests (Section4.2) we get nonzero α even for these trivial n-gram models. For example, for the English-German translation task, with M being T5-XXL11B and M being a trivial bigram model, we get α ≈ 0.2 which leads to an inference speed improvement factor of 1.25X with γ =3.

**Code links:**
- `README.md` — training entry (confidence 0.41): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, which are central to the claim.
- `ngram_assisted/ngram_assisted.py` — training entry (confidence 0.34): This file explicitly implements `ngram_assisted_speculative_generate`, which is the method described in the claim (using a bigram model as approximation).
- `sampling/codec_speculative_decoding.py` — training entry (confidence 0.34): This file contains the `autoregressive_generate_encoder_decoder` function, which is likely used for T5 models (encoder-decoder architecture) and includes logic for speculative decoding.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and measuring wall times for different decoding strategies, including ngram-assisted.

**Missing for this claim:**
- **[high] other** — The paper mentions using 'existing checkpoints' for T5 models. It is unclear if these checkpoints are publicly available or if they are internal Google checkpoints. If they are internal, reproduction would be impossible.
- **[high] data_split** — The paper mentions using existing checkpoints for models like T5-XXL, T5-small, T5-base, and T5-large, but it does not specify the exact data splits used for training or fine-tuning these models. This information is crucial for reproducing the exact performance and behavior of the models used as the target and approximation models.
- **[medium] hyperparameters** — While the paper mentions using T5-XXL, T5-small, T5-base, and T5-large models and their existing checkpoints, it does not specify the exact hyperparameters used for fine-tuning these models on the English-German translation (WMTEnDe) and CNN/DM summarization tasks. This includes learning rate, batch size (though batch size of 1 is mentioned for inference), number of epochs, optimizer, etc. The paper does mention using a batch size of 1 for inference.
- **[low] other** — The paper mentions that the T5X implementation is a 'popular optimized implementation'. To ensure a fair comparison and reproducibility, it would be helpful to specify the exact version or commit hash of the T5X implementation used.
- **[low] hardware** — The paper mentions using a single TPU-v4 for measuring walltime improvements. However, it does not specify the exact configuration or version of the TPU-v4, which could lead to variations in performance. Additionally, for the LaMDA experiments, the hardware used is not specified.

**Blockers:**
- Availability of T5-XXL model checkpoints (especially for WMTEnDe task)
- Specific T5X baseline implementation details
- Dataset (WMTEnDe) loading and preprocessing for T5 models
- Implementation details of the 'trivial bigram model' for approximation

**Notes:** The `ngram_assisted.py` file directly supports the 'trivial bigram model' aspect. However, the T5-XXL model and WMTEnDe dataset are still missing for a full reproduction.

### Claim 8

> For the GPT-like (97M params) model with argmax sampling (T=0) and a GPT-like (6M) approximation model, the alpha value is 0.88.

**Metric:** alpha · proposed 0.88
**Method:** speculative decoding vs **Baseline:** ?
**Feasibility:** `low`

**Evidence:**
> GPT-LIKE(97M) GPT-LIKE(6M) T=0 0.88

**Code links:**
- `README.md` — training entry (confidence 0.41): The README introduces the repository as a PyTorch implementation of Speculative Decoding and mentions the generation strategies, which are central to the claim.
- `sampling/speculative_decoding.py` — training entry (confidence 0.34): This file likely contains the core implementation of the speculative decoding algorithm, which would be used to calculate metrics like alpha.
- `infer.py` — eval script (confidence 0.70): As a likely entry point, 'infer.py' would be responsible for running the inference process and potentially calculating metrics like alpha.

**Missing for this claim:**
- **[medium] hyperparameters** — The paper mentions using a GPT-like Transformer decoder with 6M parameters for the approximation model and a 97M parameter model for the target model in the unconditional language generation task. However, the specific hyperparameters for these models (e.g., number of layers, attention heads, hidden dimensions, feed-forward dimensions, activation functions, dropout rates) are not fully detailed, beyond mentioning 'dim256, dim feed-forward 1024, 2 layers, 4 attention heads' for the 6M model and 'dim768, dim feed-forward 3072, 12 layers, 12 attention heads' for the 97M model. The activation function (Gelu) and tokenizer (Bert) are mentioned, but other training hyperparameters are missing.
- **[high] training_recipe** — For the GPT-like models, while some architectural details are provided, the specific training recipe (e.g., optimizer, learning rate, batch size, training duration, regularization techniques) used to train the 6M and 97M parameter models is not specified. This is crucial for understanding how the approximation and target models were created.
- **[medium] data_preprocessing** — The paper mentions using 'Bert tokenization with 8k tokens for all models' for the GPT-like models. However, details about other preprocessing steps, such as text cleaning, normalization, or any specific tokenization strategies beyond the mention of Bert tokenizer and vocabulary size, are not provided. This could impact the exact token sequences generated and thus the performance.
- **[medium] compute_budget** — While the paper discusses theoretical speedups and provides empirical results, it does not explicitly state the compute budget (e.g., total FLOPs, training time, inference time) for training the custom GPT-like models or for the experiments involving LaMDA models. This would help in understanding the overall resource requirements.
- **[low] other** — The paper mentions using 'Bert tokenization (Devlin et al., 2019) with 8k tokens for all models' for the GPT-like models. It would be beneficial to specify the exact vocabulary file or provide a link to it, as different versions or implementations of the BERT tokenizer might exist.

**Blockers:**
- Availability or clear instructions for training/obtaining GPT-like 97M and 6M models
- Specific hyperparameters for these GPT-like models
- Dataset used for unconditional language generation

**Notes:** This claim involves custom GPT-like models, which are not provided in the repository. The repository focuses on the decoding algorithms, not the models themselves. Reproducing this would require training or obtaining these specific models.

## Risks

- Missing model checkpoints: The paper relies heavily on 'existing checkpoints' for T5 and LaMDA models, which are not provided or linked, making reproduction impossible if they are proprietary.
- Missing baseline implementation details: The comparison to 'standard T5X implementation' lacks specific versioning or code, making it hard to ensure a fair comparison.
- Missing dataset details: While tasks are mentioned, the exact data splits and preprocessing for evaluation are not detailed, especially for the T5 models.
- Missing custom model training details: For GPT-like models, the training recipes and full hyperparameters are not provided, making it impossible to recreate them.
- Hardware specificity: Wall-time measurements are highly dependent on hardware, and the specific TPU-v4 configuration is not detailed.

## Next Steps

1. Identify if the T5 and LaMDA model checkpoints are publicly available and link them.
2. Obtain or implement the exact T5X baseline used for comparison.
3. Provide detailed instructions or scripts for dataset loading and preprocessing for WMTEnDe and CNN/DM.
4. Provide full training recipes and hyperparameters for the GPT-like models, or provide pre-trained checkpoints.
5. Clarify the exact hardware configuration used for wall-time measurements.
