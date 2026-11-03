# Agreement in the centered Qwen space (exploratory)

524 unique cleaned descriptors; model Qwen/Qwen3-Embedding-0.6B, instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'; embeddings centered on the occurrence-weighted descriptor mean; chance = 2000 shuffles; CI and p = participant bootstrap / condition swap with 1000 iterations; seed 42.

## Kappa per condition

| Field | Condition | Descriptors | Observed | Expected | Kappa [95% CI] |
|---|---|---:|---:|---:|---|
| notesaroma | stimulation | 183 | 0.074 | 0.005 | 0.070 [0.038, 0.105] |
| notesaroma | sham | 178 | 0.077 | 0.009 | 0.069 [0.041, 0.100] |
| flavor_notes | stimulation | 184 | 0.054 | -0.002 | 0.055 [0.032, 0.084] |
| flavor_notes | sham | 182 | 0.071 | 0.007 | 0.065 [0.033, 0.100] |

## Stimulation vs sham

| Field | Stimulation | Sham | Delta [95% CI] | p | q (BH) |
|---|---:|---:|---|---:|---:|
| notesaroma | 0.070 | 0.069 | +0.001 [-0.034, +0.041] | 0.95 | 0.95 |
| flavor_notes | 0.055 | 0.064 | -0.009 [-0.042, +0.024] | 0.58 | 0.95 |
