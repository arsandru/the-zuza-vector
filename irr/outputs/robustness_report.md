# Robustness of the semantic IRR (exploratory)

Seed 42 is the reported analysis; seeds 1, 2, 3 repeat it with the same settings (2000 chance shuffles, 1000 bootstrap / swap iterations, 100 chance shuffles inside each resample).

## 1. Spread of each quantity across seeds

| Space | Field | Condition | Quantity | Seed 42 (reported) | Min | Max | Range |
|---|---|---|---|---:|---:|---:|---:|
| centered (main) | notesaroma | stimulation | kappa | 0.070 | 0.070 | 0.070 | 0.000 |
| centered (main) | notesaroma | sham | kappa | 0.069 | 0.069 | 0.069 | 0.000 |
| centered (main) | notesaroma | stimulation - sham | delta | 0.001 | 0.001 | 0.001 | 0.000 |
| centered (main) | notesaroma | stimulation - sham | p | 0.950 | 0.944 | 0.957 | 0.013 |
| centered (main) | flavor_notes | stimulation | kappa | 0.055 | 0.055 | 0.056 | 0.000 |
| centered (main) | flavor_notes | sham | kappa | 0.065 | 0.064 | 0.065 | 0.000 |
| centered (main) | flavor_notes | stimulation - sham | delta | -0.009 | -0.009 | -0.009 | 0.000 |
| centered (main) | flavor_notes | stimulation - sham | p | 0.581 | 0.572 | 0.603 | 0.031 |
| plain (sensitivity) | notesaroma | stimulation | kappa | 0.068 | 0.068 | 0.068 | 0.000 |
| plain (sensitivity) | notesaroma | sham | kappa | 0.068 | 0.068 | 0.068 | 0.000 |
| plain (sensitivity) | notesaroma | stimulation - sham | delta | 0.000 | 0.000 | 0.001 | 0.000 |
| plain (sensitivity) | notesaroma | stimulation - sham | p | 0.992 | 0.982 | 0.998 | 0.016 |
| plain (sensitivity) | flavor_notes | stimulation | kappa | 0.057 | 0.057 | 0.057 | 0.000 |
| plain (sensitivity) | flavor_notes | sham | kappa | 0.063 | 0.062 | 0.063 | 0.000 |
| plain (sensitivity) | flavor_notes | stimulation - sham | delta | -0.006 | -0.006 | -0.006 | 0.000 |
| plain (sensitivity) | flavor_notes | stimulation - sham | p | 0.719 | 0.695 | 0.740 | 0.045 |
| centered (main) | notesaroma | stimulation - sham | q | 0.950 | 0.944 | 0.957 | 0.013 |
| centered (main) | flavor_notes | stimulation - sham | q | 0.950 | 0.944 | 0.957 | 0.013 |
| plain (sensitivity) | notesaroma | stimulation - sham | q | 0.992 | 0.982 | 0.998 | 0.016 |
| plain (sensitivity) | flavor_notes | stimulation - sham | q | 0.992 | 0.982 | 0.998 | 0.016 |

Largest range across seeds for kappa: point estimate 0.0004, lower interval limit 0.0026.

Largest range across seeds for delta: point estimate 0.0005, lower interval limit 0.0024.

## 2. Semantic kappa per tasting (centered space; chance level of the whole condition; participant-bootstrap CI)

| Field | Tasting | Stimulation | Sham |
|---|---|---|---|
| notesaroma | Brasil #1 | 0.117 [0.021, 0.240] | 0.117 [0.031, 0.219] |
| notesaroma | Brasil #2 | 0.105 [0.050, 0.180] | 0.106 [0.011, 0.226] |
| notesaroma | Brasil #3 | 0.135 [0.079, 0.197] | 0.078 [0.001, 0.169] |
| notesaroma | Kenya #1 | -0.006 [-0.037, 0.048] | 0.006 [-0.033, 0.057] |
| notesaroma | Kenya #2 | 0.055 [-0.004, 0.134] | 0.041 [-0.014, 0.116] |
| notesaroma | Kenya #3 | 0.017 [-0.017, 0.074] | 0.060 [-0.002, 0.128] |
| flavor_notes | Brasil #1 | 0.032 [-0.011, 0.092] | -0.003 [-0.037, 0.065] |
| flavor_notes | Brasil #2 | 0.048 [-0.008, 0.123] | 0.054 [-0.018, 0.147] |
| flavor_notes | Brasil #3 | 0.031 [-0.017, 0.115] | 0.022 [-0.020, 0.082] |
| flavor_notes | Kenya #1 | 0.038 [-0.004, 0.108] | 0.094 [0.014, 0.193] |
| flavor_notes | Kenya #2 | 0.102 [0.021, 0.200] | 0.108 [0.015, 0.219] |
| flavor_notes | Kenya #3 | 0.087 [0.015, 0.180] | 0.096 [0.009, 0.208] |
