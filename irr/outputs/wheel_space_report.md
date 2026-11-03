# Agreement in a flavor-wheel space (exploratory)

105 wheel anchors (terms, category names, family names), 524 unique cleaned descriptors; model Qwen/Qwen3-Embedding-0.6B; chance = 2000 shuffles; CI and p = participant bootstrap / condition swap with 1000 iterations; seed 42.

## Space check on wheel terms (the two terms of a pair are removed from the anchors)

| Space | Term pairs | AUC same family | AUC same category | Mean sim. same family | Mean sim. other |
|---|---:|---:|---:|---:|---:|
| Qwen (plain) | 2485 | 0.712 | 0.731 | 0.700 | 0.640 |
| Qwen (centered on descriptor mean) | 2485 | 0.774 | 0.817 | 0.204 | 0.038 |
| wheel space | 2485 | 0.732 | 0.762 | 0.369 | 0.065 |

## Kappa per condition

| Field | Condition | Descriptors | Observed | Expected | Kappa [95% CI] |
|---|---|---:|---:|---:|---|
| notesaroma | stimulation | 183 | 0.132 | 0.026 | 0.109 [0.060, 0.167] |
| notesaroma | sham | 178 | 0.130 | 0.030 | 0.103 [0.054, 0.160] |
| flavor_notes | stimulation | 184 | 0.088 | -0.003 | 0.091 [0.047, 0.143] |
| flavor_notes | sham | 182 | 0.107 | 0.006 | 0.102 [0.055, 0.156] |

## Stimulation vs sham

| Field | Stimulation | Sham | Delta [95% CI] | p | q (BH) |
|---|---:|---:|---|---:|---:|
| notesaroma | 0.109 | 0.103 | +0.006 [-0.052, +0.073] | 0.86 | 0.86 |
| flavor_notes | 0.091 | 0.101 | -0.010 [-0.063, +0.045] | 0.68 | 0.86 |
