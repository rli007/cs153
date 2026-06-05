# Bench: real-papers-v1

Five real, well-known ML papers spanning the reproducibility quality spectrum. Hand-curated ground truth based on author repos and what is/is not in each paper.

## Aggregate

- claim_coverage: 0.800
- gap_f1: 0.292
- link_accuracy: 1.000
- feasibility_pass_rate: 0.600
- overall: 0.673

## Per-paper

### lora
- claim_coverage=1.000 · gap_f1=0.250 · link_accuracy=1.000 · feasibility_pass=True · aggregate=0.812
- notes:
  - gap_detection: did not flag ['compute_budget']
  - gap_detection: extra (possibly false-positive) flags: ['data_split', 'hardware', 'hyperparameters', 'other', 'training_recipe']

### flash-attention
- claim_coverage=1.000 · gap_f1=0.444 · link_accuracy=1.000 · feasibility_pass=True · aggregate=0.861
- notes:
  - gap_detection: extra (possibly false-positive) flags: ['compute_budget', 'data_preprocessing', 'data_split', 'hyperparameters', 'training_recipe']

### dpo
- claim_coverage=1.000 · gap_f1=0.182 · link_accuracy=1.000 · feasibility_pass=False · aggregate=0.545
- notes:
  - gap_detection: extra (possibly false-positive) flags: ['checkpoint', 'compute_budget', 'data_preprocessing', 'data_split', 'evaluation_script', 'hardware', 'hyperparameters', 'license', 'training_recipe']
  - feasibility: got low, expected >= medium

### mamba
- claim_coverage=0.500 · gap_f1=0.250 · link_accuracy=1.000 · feasibility_pass=False · aggregate=0.438
- notes:
  - missing claim with keywords ['Mamba', 'selective']
  - gap_detection: did not flag ['random_seed']
  - gap_detection: extra (possibly false-positive) flags: ['compute_budget', 'data_split', 'hyperparameters', 'other', 'training_recipe']
  - feasibility: got low, expected >= medium

### qlora
- claim_coverage=0.500 · gap_f1=0.333 · link_accuracy=1.000 · feasibility_pass=True · aggregate=0.708
- notes:
  - missing claim with keywords ['QLoRA', '4-bit']
  - gap_detection: extra (possibly false-positive) flags: ['compute_budget', 'data_preprocessing', 'data_split', 'evaluation_script', 'hardware', 'hyperparameters', 'license', 'training_recipe']
