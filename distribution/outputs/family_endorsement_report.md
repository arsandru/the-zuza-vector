# Family endorsement, stimulation vs sham (exploratory)

Participants = unit; 10000 sign-flip permutations, 10000 bootstrap draws, seed 42. Rates are endorsements per non-missing tasting.

## Omnibus (sum of squared paired t over the 9 families)

| Field | n | T | Null mean (p95) | p | q (BH, 2 fields) |
|---|---:|---:|---|---:|---:|
| notesaroma | 32 | 21.71 | 9.65 (18.49) | 0.018 | 0.035 |
| flavor_notes | 33 | 8.35 | 9.66 (18.50) | 0.542 | 0.542 |

## Per family (difference = stimulation - sham, endorsement rate)

| Field | Family | Stimulation | Sham | Difference [95% CI] | t | p | q (BH, 18 tests) |
|---|---|---:|---:|---|---:|---:|---:|
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | -2.24 | 0.042 | 0.251 |
| notesaroma | fruity | 0.33 | 0.32 | +0.01 [-0.07, +0.11] | +0.32 | 0.765 | 1.000 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.06 [+0.00, +0.12] | +1.86 | 0.081 | 0.290 |
| notesaroma | green/vegetative | 0.07 | 0.14 | -0.07 [-0.13, -0.02] | -2.37 | 0.020 | 0.251 |
| notesaroma | other (wheel family 5: chemical, papery/musty) | 0.03 | 0.03 | +0.00 [-0.04, +0.05] | +0.12 | 1.000 | 1.000 |
| notesaroma | roasted | 0.26 | 0.29 | -0.03 [-0.12, +0.06] | -0.70 | 0.500 | 0.901 |
| notesaroma | spices | 0.08 | 0.11 | -0.03 [-0.07, +0.01] | -1.50 | 0.187 | 0.482 |
| notesaroma | nutty/cocoa | 0.38 | 0.39 | -0.01 [-0.10, +0.08] | -0.20 | 0.865 | 1.000 |
| notesaroma | sweet | 0.23 | 0.14 | +0.08 [+0.01, +0.15] | +2.18 | 0.041 | 0.251 |
| flavor_notes | floral | 0.11 | 0.07 | +0.04 [-0.02, +0.09] | +1.31 | 0.225 | 0.507 |
| flavor_notes | fruity | 0.49 | 0.46 | +0.02 [-0.08, +0.12] | +0.42 | 0.688 | 1.000 |
| flavor_notes | sour/fermented | 0.26 | 0.27 | -0.01 [-0.09, +0.07] | -0.29 | 0.792 | 1.000 |
| flavor_notes | green/vegetative | 0.10 | 0.08 | +0.02 [-0.02, +0.06] | +0.92 | 0.395 | 0.789 |
| flavor_notes | other (wheel family 5: chemical, papery/musty) | 0.08 | 0.08 | +0.00 [-0.05, +0.06] | +0.07 | 1.000 | 1.000 |
| flavor_notes | roasted | 0.29 | 0.21 | +0.08 [-0.00, +0.16] | +1.87 | 0.074 | 0.290 |
| flavor_notes | spices | 0.09 | 0.08 | +0.01 [-0.05, +0.07] | +0.36 | 0.747 | 1.000 |
| flavor_notes | nutty/cocoa | 0.35 | 0.30 | +0.05 [-0.02, +0.13] | +1.37 | 0.187 | 0.482 |
| flavor_notes | sweet | 0.12 | 0.12 | +0.00 [-0.06, +0.07] | +0.09 | 0.929 | 1.000 |

## Does the condition effect vary across tastings? (sum over families of the repeated-measures F)

| Field | n | sum F | Null mean (p95) | p |
|---|---:|---:|---|---:|
| notesaroma | 30 | 3.56 | 9.30 (15.06) | 0.991 |
| flavor_notes | 27 | 12.07 | 9.36 (14.98) | 0.179 |
