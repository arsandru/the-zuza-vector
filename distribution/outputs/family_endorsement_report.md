# Family endorsement, stimulation vs sham (exploratory)

Participants = unit; 10000 sign-flip permutations, 10000 bootstrap draws, seed 42. Rates are endorsements per non-missing tasting.

## Omnibus (sum of squared paired t over the 9 families)

| Field | n | T | Null mean (p95) | p | q (BH, 2 fields) |
|---|---:|---:|---|---:|---:|
| notesaroma | 32 | 19.84 | 9.66 (18.26) | 0.031 | 0.062 |
| flavor_notes | 33 | 8.36 | 9.65 (18.57) | 0.543 | 0.543 |

## Per family (difference = stimulation - sham, endorsement rate)

| Field | Family | Stimulation | Sham | Difference [95% CI] | t | p | q (BH, 18 tests) |
|---|---|---:|---:|---|---:|---:|---:|
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | -2.30 | 0.040 | 0.321 |
| notesaroma | fruity | 0.33 | 0.32 | +0.01 [-0.07, +0.10] | +0.25 | 0.829 | 0.932 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.05 [-0.00, +0.11] | +1.78 | 0.100 | 0.359 |
| notesaroma | green/vegetative | 0.07 | 0.13 | -0.06 [-0.12, -0.00] | -1.89 | 0.071 | 0.321 |
| notesaroma | other (wheel family 5: chemical, papery/musty) | 0.03 | 0.03 | +0.00 [-0.04, +0.05] | +0.12 | 1.000 | 1.000 |
| notesaroma | roasted | 0.25 | 0.27 | -0.02 [-0.10, +0.06] | -0.39 | 0.721 | 0.932 |
| notesaroma | spices | 0.07 | 0.11 | -0.03 [-0.07, +0.01] | -1.66 | 0.176 | 0.482 |
| notesaroma | nutty/cocoa | 0.38 | 0.39 | -0.01 [-0.10, +0.07] | -0.31 | 0.754 | 0.932 |
| notesaroma | sweet | 0.22 | 0.14 | +0.08 [+0.01, +0.15] | +2.18 | 0.040 | 0.321 |
| notesaroma | unmapped (no wheel home; descriptive only) | 0.03 | 0.05 | -0.02 [-0.07, +0.02] | - | - | - |
| flavor_notes | floral | 0.11 | 0.07 | +0.04 [-0.02, +0.09] | +1.31 | 0.225 | 0.507 |
| flavor_notes | fruity | 0.48 | 0.46 | +0.02 [-0.08, +0.11] | +0.33 | 0.753 | 0.932 |
| flavor_notes | sour/fermented | 0.25 | 0.27 | -0.02 [-0.09, +0.06] | -0.37 | 0.730 | 0.932 |
| flavor_notes | green/vegetative | 0.10 | 0.08 | +0.02 [-0.03, +0.06] | +0.82 | 0.451 | 0.902 |
| flavor_notes | other (wheel family 5: chemical, papery/musty) | 0.08 | 0.08 | +0.01 [-0.05, +0.06] | +0.18 | 0.925 | 0.980 |
| flavor_notes | roasted | 0.29 | 0.21 | +0.08 [-0.00, +0.16] | +1.90 | 0.067 | 0.321 |
| flavor_notes | spices | 0.09 | 0.08 | +0.01 [-0.05, +0.07] | +0.36 | 0.747 | 0.932 |
| flavor_notes | nutty/cocoa | 0.35 | 0.30 | +0.05 [-0.02, +0.13] | +1.37 | 0.187 | 0.482 |
| flavor_notes | sweet | 0.12 | 0.12 | +0.01 [-0.05, +0.07] | +0.24 | 0.820 | 0.932 |
| flavor_notes | unmapped (no wheel home; descriptive only) | 0.04 | 0.05 | -0.01 [-0.04, +0.02] | - | - | - |

## Does the condition effect vary across tastings? (sum over families of the repeated-measures F)

| Field | n | sum F | Null mean (p95) | p |
|---|---:|---:|---|---:|
| notesaroma | 30 | 2.76 | 9.29 (15.04) | 0.998 |
| flavor_notes | 27 | 11.44 | 9.36 (15.03) | 0.226 |
