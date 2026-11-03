# Agreement after mapping to the SCA flavor wheel (exploratory)

Model Qwen/Qwen3-Embedding-0.6B with instruction 'Instruct: Embed aroma/flavor descriptors.\nText:' for the embedding measure; chance = 2000 shuffles; CI and p = participant bootstrap / condition swap with 1000 iterations; seed 42.

## Coverage

| Variant | Field | Descriptors after main cleaning | Mapped (non-empty) | Participants with any |
|---|---|---:|---:|---:|
| other kept (5_other) | notesaroma | 361 | 361 | 33 |
| other kept (5_other) | flavor_notes | 366 | 366 | 34 |
| other dropped | notesaroma | 361 | 354 | 33 |
| other dropped | flavor_notes | 366 | 364 | 34 |

## Kappa per condition

| Variant | Measure | Field | Condition | Descriptors | Observed | Expected | Kappa [95% CI] |
|---|---|---|---|---:|---:|---:|---|
| other kept (5_other) | embedding | notesaroma | stimulation | 183 | 0.685 | 0.660 | 0.073 [0.042, 0.112] |
| other kept (5_other) | embedding | notesaroma | sham | 178 | 0.682 | 0.655 | 0.080 [0.051, 0.108] |
| other kept (5_other) | embedding | flavor_notes | stimulation | 184 | 0.678 | 0.657 | 0.060 [0.035, 0.090] |
| other kept (5_other) | embedding | flavor_notes | sham | 182 | 0.670 | 0.649 | 0.060 [0.033, 0.092] |
| other kept (5_other) | node Jaccard | notesaroma | stimulation | 183 | 0.048 | 0.032 | 0.016 [0.009, 0.025] |
| other kept (5_other) | node Jaccard | notesaroma | sham | 178 | 0.054 | 0.037 | 0.018 [0.007, 0.029] |
| other kept (5_other) | node Jaccard | flavor_notes | stimulation | 184 | 0.052 | 0.041 | 0.011 [0.004, 0.021] |
| other kept (5_other) | node Jaccard | flavor_notes | sham | 182 | 0.055 | 0.044 | 0.011 [0.003, 0.020] |
| other kept (5_other) | family Jaccard | notesaroma | stimulation | 183 | 0.254 | 0.180 | 0.090 [0.050, 0.139] |
| other kept (5_other) | family Jaccard | notesaroma | sham | 178 | 0.240 | 0.176 | 0.078 [0.049, 0.114] |
| other kept (5_other) | family Jaccard | flavor_notes | stimulation | 184 | 0.260 | 0.206 | 0.068 [0.036, 0.106] |
| other kept (5_other) | family Jaccard | flavor_notes | sham | 182 | 0.254 | 0.204 | 0.064 [0.034, 0.094] |
| other dropped | embedding | notesaroma | stimulation | 180 | 0.685 | 0.660 | 0.074 [0.042, 0.114] |
| other dropped | embedding | notesaroma | sham | 174 | 0.683 | 0.655 | 0.082 [0.053, 0.113] |
| other dropped | embedding | flavor_notes | stimulation | 183 | 0.678 | 0.657 | 0.061 [0.036, 0.091] |
| other dropped | embedding | flavor_notes | sham | 181 | 0.671 | 0.650 | 0.061 [0.033, 0.094] |
| other dropped | node Jaccard | notesaroma | stimulation | 180 | 0.048 | 0.033 | 0.016 [0.008, 0.025] |
| other dropped | node Jaccard | notesaroma | sham | 174 | 0.057 | 0.039 | 0.019 [0.007, 0.032] |
| other dropped | node Jaccard | flavor_notes | stimulation | 183 | 0.053 | 0.042 | 0.012 [0.004, 0.021] |
| other dropped | node Jaccard | flavor_notes | sham | 181 | 0.056 | 0.045 | 0.012 [0.003, 0.021] |
| other dropped | family Jaccard | notesaroma | stimulation | 180 | 0.261 | 0.187 | 0.092 [0.050, 0.142] |
| other dropped | family Jaccard | notesaroma | sham | 174 | 0.254 | 0.185 | 0.084 [0.054, 0.120] |
| other dropped | family Jaccard | flavor_notes | stimulation | 183 | 0.264 | 0.208 | 0.071 [0.039, 0.110] |
| other dropped | family Jaccard | flavor_notes | sham | 181 | 0.258 | 0.206 | 0.065 [0.036, 0.096] |

## Stimulation vs sham

| Variant | Measure | Field | Stimulation | Sham | Delta [95% CI] | p |
|---|---|---|---:|---:|---|---:|
| other kept (5_other) | embedding | notesaroma | 0.073 | 0.080 | -0.006 [-0.043, +0.034] | 0.78 |
| other kept (5_other) | embedding | flavor_notes | 0.060 | 0.060 | +0.000 [-0.030, +0.032] | 0.99 |
| other kept (5_other) | node Jaccard | notesaroma | 0.016 | 0.018 | -0.001 [-0.014, +0.011] | 0.83 |
| other kept (5_other) | node Jaccard | flavor_notes | 0.011 | 0.011 | +0.000 [-0.010, +0.011] | 0.98 |
| other kept (5_other) | family Jaccard | notesaroma | 0.090 | 0.078 | +0.012 [-0.040, +0.070] | 0.67 |
| other kept (5_other) | family Jaccard | flavor_notes | 0.068 | 0.063 | +0.005 [-0.033, +0.045] | 0.80 |
| other dropped | embedding | notesaroma | 0.074 | 0.082 | -0.008 [-0.046, +0.033] | 0.71 |
| other dropped | embedding | flavor_notes | 0.061 | 0.061 | -0.000 [-0.031, +0.032] | 0.99 |
| other dropped | node Jaccard | notesaroma | 0.016 | 0.019 | -0.003 [-0.016, +0.010] | 0.63 |
| other dropped | node Jaccard | flavor_notes | 0.012 | 0.012 | +0.000 [-0.011, +0.012] | 0.94 |
| other dropped | family Jaccard | notesaroma | 0.092 | 0.084 | +0.008 [-0.046, +0.068] | 0.78 |
| other dropped | family Jaccard | flavor_notes | 0.071 | 0.065 | +0.006 [-0.033, +0.047] | 0.75 |
