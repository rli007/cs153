# Bench: real-papers-v1

Five real, well-known ML papers spanning the reproducibility quality spectrum. Hand-curated ground truth based on author repos and what is/is not in each paper.

## Aggregate

- claim_coverage: 0.800
- gap_f1: 0.228
- link_accuracy: 1.000
- feasibility_pass_rate: 0.200
- overall: 0.557

## Per-paper

### lora
- claim_coverage=1.000 · gap_f1=0.286 · link_accuracy=1.000 · feasibility_pass=False · aggregate=0.571
- notes:
  - gap_detection: did not flag ['random_seed']
  - gap_detection: extra (possibly false-positive) flags: ['data_split', 'hyperparameters', 'other', 'training_recipe']
  - feasibility: got low, expected >= medium

### flash-attention
- claim_coverage=1.000 · gap_f1=0.308 · link_accuracy=1.000 · feasibility_pass=False · aggregate=0.577
- notes:
  - gap_detection: extra (possibly false-positive) flags: ['checkpoint', 'compute_budget', 'data_preprocessing', 'data_split', 'evaluation_script', 'hyperparameters', 'license', 'other', 'training_recipe']
  - feasibility: got low, expected >= medium

### dpo
- claim_coverage=1.000 · gap_f1=0.182 · link_accuracy=1.000 · feasibility_pass=False · aggregate=0.545
- notes:
  - gap_detection: extra (possibly false-positive) flags: ['checkpoint', 'compute_budget', 'data_preprocessing', 'data_split', 'evaluation_script', 'hardware', 'hyperparameters', 'license', 'training_recipe']
  - feasibility: got low, expected >= medium

### mamba
- claim_coverage=0.500 · gap_f1=0.364 · link_accuracy=1.000 · feasibility_pass=False · aggregate=0.466
- notes:
  - missing claim with keywords ['Mamba', 'selective']
  - gap_detection: extra (possibly false-positive) flags: ['checkpoint', 'compute_budget', 'data_preprocessing', 'data_split', 'evaluation_script', 'hyperparameters', 'training_recipe']
  - feasibility: got low, expected >= medium

### qlora
- claim_coverage=0.500 · gap_f1=0.000 · link_accuracy=1.000 · feasibility_pass=True · aggregate=0.625
- notes:
  - missing claim with keywords ['QLoRA', '4-bit']
  - gap_detection: did not flag ['checkpoint', 'random_seed']
  - gap_detection: extra (possibly false-positive) flags: ['hyperparameters', 'training_recipe']
