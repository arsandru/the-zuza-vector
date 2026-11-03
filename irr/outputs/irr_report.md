# Between-participant semantic agreement, stimulation vs sham (exploratory)

34 participants; items = coffee x repeated tasting (6 per condition); 524 unique cleaned descriptors; model Qwen/Qwen3-Embedding-0.6B, instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'. Main space = embeddings centered on the descriptor mean; sensitivity = plain embeddings. Chance = 2000 shuffles; CI and p = participant bootstrap / condition swap with 1000 iterations; seed 42.

## Kappa per condition

| Space | Field | Condition | Participants | Descriptors | Observed | Expected | Kappa [95% CI] |
|---|---|---|---:|---:|---:|---:|---|
| centered (main) | notesaroma | stimulation | 34 | 183 | 0.074 | 0.005 | 0.070 [0.038, 0.105] |
| centered (main) | notesaroma | sham | 34 | 178 | 0.077 | 0.009 | 0.069 [0.041, 0.100] |
| centered (main) | flavor_notes | stimulation | 34 | 184 | 0.054 | -0.002 | 0.055 [0.032, 0.084] |
| centered (main) | flavor_notes | sham | 34 | 182 | 0.071 | 0.007 | 0.065 [0.033, 0.100] |
| plain (sensitivity) | notesaroma | stimulation | 34 | 183 | 0.678 | 0.655 | 0.068 [0.037, 0.104] |
| plain (sensitivity) | notesaroma | sham | 34 | 178 | 0.678 | 0.655 | 0.068 [0.041, 0.097] |
| plain (sensitivity) | flavor_notes | stimulation | 34 | 184 | 0.666 | 0.646 | 0.057 [0.033, 0.086] |
| plain (sensitivity) | flavor_notes | sham | 34 | 182 | 0.668 | 0.646 | 0.063 [0.033, 0.096] |

## Stimulation vs sham

| Space | Field | Stimulation | Sham | Delta [95% CI] | p | q (BH, 2 fields) |
|---|---|---:|---:|---|---:|---:|
| centered (main) | notesaroma | 0.070 | 0.069 | +0.001 [-0.034, +0.041] | 0.95 | 0.95 |
| centered (main) | flavor_notes | 0.055 | 0.064 | -0.009 [-0.042, +0.024] | 0.58 | 0.95 |
| plain (sensitivity) | notesaroma | 0.068 | 0.068 | +0.000 [-0.033, +0.039] | 0.99 | 0.99 |
| plain (sensitivity) | flavor_notes | 0.057 | 0.062 | -0.006 [-0.038, +0.027] | 0.72 | 0.99 |
