# Family endorsement, stimulation vs sham (exploratory)

Participants = unit; 10000 sign-flip permutations, 10000 bootstrap draws, seed 42. Rates are endorsements per non-missing tasting.

## Omnibus (sum of squared paired t over the 9 families)

| Field | n | T | Null mean (p95) | p | Holm p |
|---|---:|---:|---|---:|---:|
| notesaroma | 32 | 19.94 | 9.69 (18.62) | 0.035 | 0.070 |
| flavor_notes | 33 | 8.38 | 9.64 (18.45) | 0.542 | 0.542 |

## Per family (difference = stimulation - sham, endorsement rate)

| Field | Family | Stimulation | Sham | Difference [95% CI] | t | p | p (max-t, 18 tests) |
|---|---|---:|---:|---|---:|---:|---:|
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | -2.30 | 0.040 | 0.388 |
| notesaroma | fruity | 0.33 | 0.32 | +0.01 [-0.07, +0.10] | +0.25 | 0.829 | 1.000 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.05 [-0.00, +0.11] | +1.78 | 0.100 | 0.791 |
| notesaroma | green/vegetative | 0.07 | 0.13 | -0.06 [-0.12, -0.00] | -1.89 | 0.071 | 0.714 |
| notesaroma | other (5, incl. unmapped words) | 0.06 | 0.07 | -0.01 [-0.07, +0.05] | -0.35 | 0.755 | 1.000 |
| notesaroma | roasted | 0.25 | 0.27 | -0.02 [-0.10, +0.06] | -0.39 | 0.721 | 1.000 |
| notesaroma | spices | 0.07 | 0.11 | -0.03 [-0.07, +0.01] | -1.66 | 0.176 | 0.883 |
| notesaroma | nutty/cocoa | 0.38 | 0.39 | -0.01 [-0.10, +0.07] | -0.31 | 0.754 | 1.000 |
| notesaroma | sweet | 0.22 | 0.14 | +0.08 [+0.01, +0.15] | +2.18 | 0.040 | 0.480 |
| flavor_notes | floral | 0.11 | 0.07 | +0.04 [-0.02, +0.09] | +1.31 | 0.225 | 0.982 |
| flavor_notes | fruity | 0.48 | 0.46 | +0.02 [-0.08, +0.11] | +0.33 | 0.753 | 1.000 |
| flavor_notes | sour/fermented | 0.25 | 0.27 | -0.02 [-0.09, +0.06] | -0.37 | 0.730 | 1.000 |
| flavor_notes | green/vegetative | 0.10 | 0.08 | +0.02 [-0.03, +0.06] | +0.82 | 0.451 | 1.000 |
| flavor_notes | other (5, incl. unmapped words) | 0.12 | 0.11 | +0.01 [-0.05, +0.06] | +0.22 | 0.858 | 1.000 |
| flavor_notes | roasted | 0.29 | 0.21 | +0.08 [-0.00, +0.16] | +1.90 | 0.067 | 0.698 |
| flavor_notes | spices | 0.09 | 0.08 | +0.01 [-0.05, +0.07] | +0.36 | 0.747 | 1.000 |
| flavor_notes | nutty/cocoa | 0.35 | 0.30 | +0.05 [-0.02, +0.13] | +1.37 | 0.187 | 0.972 |
| flavor_notes | sweet | 0.12 | 0.12 | +0.01 [-0.05, +0.07] | +0.24 | 0.820 | 1.000 |

## Does the condition effect vary across tastings? (sum over families of the repeated-measures F)

| Field | n | sum F | Null mean (p95) | p |
|---|---:|---:|---|---:|
| notesaroma | 30 | 3.21 | 9.30 (15.13) | 0.995 |
| flavor_notes | 27 | 11.99 | 9.37 (15.20) | 0.187 |
