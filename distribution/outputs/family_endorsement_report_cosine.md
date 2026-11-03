# Family endorsement, stimulation vs sham (exploratory)

Participants = unit; 10000 sign-flip permutations, 10000 bootstrap draws, seed 42. Rates are endorsements per non-missing tasting.

## Omnibus (sum of squared paired t over the 9 families)

| Field | n | T | Null mean (p95) | p | q (BH, 2 fields) |
|---|---:|---:|---|---:|---:|
| notesaroma | 32 | 19.88 | 9.63 (18.24) | 0.028 | 0.057 |
| flavor_notes | 33 | 9.82 | 9.64 (18.34) | 0.418 | 0.418 |

## Per family (difference = stimulation - sham, endorsement rate)

| Field | Family | Stimulation | Sham | Difference [95% CI] | t | p | q (BH, 18 tests) |
|---|---|---:|---:|---|---:|---:|---:|
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | -2.24 | 0.042 | 0.278 |
| notesaroma | fruity | 0.34 | 0.34 | -0.00 [-0.09, +0.09] | -0.02 | 1.000 | 1.000 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.05 [-0.01, +0.11] | +1.67 | 0.114 | 0.368 |
| notesaroma | green/vegetative | 0.06 | 0.13 | -0.06 [-0.13, -0.01] | -2.06 | 0.046 | 0.278 |
| notesaroma | other (wheel family 5: chemical, papery/musty) | 0.03 | 0.02 | +0.01 [-0.03, +0.05] | +0.39 | 0.816 | 0.924 |
| notesaroma | roasted | 0.26 | 0.29 | -0.04 [-0.13, +0.05] | -0.81 | 0.438 | 0.789 |
| notesaroma | spices | 0.08 | 0.11 | -0.03 [-0.07, +0.01] | -1.50 | 0.187 | 0.421 |
| notesaroma | nutty/cocoa | 0.38 | 0.39 | -0.01 [-0.10, +0.08] | -0.20 | 0.865 | 0.924 |
| notesaroma | sweet | 0.23 | 0.14 | +0.08 [+0.01, +0.15] | +2.18 | 0.041 | 0.278 |
| flavor_notes | floral | 0.10 | 0.07 | +0.03 [-0.03, +0.09] | +1.11 | 0.306 | 0.611 |
| flavor_notes | fruity | 0.49 | 0.47 | +0.02 [-0.08, +0.11] | +0.32 | 0.758 | 0.924 |
| flavor_notes | sour/fermented | 0.26 | 0.27 | -0.01 [-0.09, +0.07] | -0.29 | 0.792 | 0.924 |
| flavor_notes | green/vegetative | 0.09 | 0.05 | +0.04 [+0.00, +0.07] | +1.88 | 0.077 | 0.346 |
| flavor_notes | other (wheel family 5: chemical, papery/musty) | 0.10 | 0.08 | +0.02 [-0.04, +0.08] | +0.56 | 0.605 | 0.924 |
| flavor_notes | roasted | 0.29 | 0.22 | +0.07 [-0.01, +0.15] | +1.61 | 0.123 | 0.368 |
| flavor_notes | spices | 0.09 | 0.08 | +0.01 [-0.05, +0.07] | +0.19 | 0.872 | 0.924 |
| flavor_notes | nutty/cocoa | 0.35 | 0.30 | +0.05 [-0.02, +0.13] | +1.37 | 0.187 | 0.421 |
| flavor_notes | sweet | 0.13 | 0.12 | +0.01 [-0.05, +0.07] | +0.25 | 0.807 | 0.924 |

## Does the condition effect vary across tastings? (sum over families of the repeated-measures F)

| Field | n | sum F | Null mean (p95) | p |
|---|---:|---:|---|---:|
| notesaroma | 30 | 2.66 | 9.29 (15.23) | 0.999 |
| flavor_notes | 27 | 15.00 | 9.39 (15.04) | 0.051 |
