# distribution: do stimulation and sham endorse different wheel-family profiles? (exploratory)

Descriptors are cleaned (main pipeline of `irr/`) and mapped to the SCA flavor wheel (`wheel_mapping.py`, `data/SCA flavor wheel.csv`, `data/sca_aliases.csv`). Words with no wheel home go to a separate catch-all, `unmapped`; it is not the wheel's own family 5 (`5_other`: chemical, papery/musty), which only receives words that really map there. Multiplicity: Benjamini-Hochberg FDR (q) within each family of tests.

## Main analysis: family endorsement (`family_endorsement.py`)

Run from the repository root: `python3 distribution/family_endorsement.py` (10000 sign-flip permutations and bootstrap draws, seed 42). The docstring defines the method.

Check-all-that-apply design: at each tasting (2 coffees x 3 repeated tastings per condition) a participant endorses a wheel family if any word of the descriptor maps to it; a tasting without a descriptor ("n\\a") is missing, not "not endorsed". The unit is the participant: endorsement rate = endorsed / non-missing tastings, per condition, field and family; paired difference d = stimulation - sham, with participants who have no usable tasting in a condition left out of that field (aroma n = 32, flavor n = 33). Only the 9 wheel families are tested; the rate of `unmapped` is reported descriptively.

1. Omnibus per field: T = sum over the 9 wheel families of the squared paired t, judged against a paired sign-flip permutation (each participant's stimulation and sham labels swapped with probability 1/2). BH-FDR q over the 2 fields.
2. Per family: mean difference in endorsement rate with a participant-bootstrap 95% CI, unadjusted sign-flip p, and BH-FDR q over the 2 x 9 family tests.
3. Does the condition effect vary across the 3 tastings? Sum over families of the repeated-measures F of the per-tasting difference, null from permuting tasting labels within participant (participants with all three tastings usable: aroma 30, flavor 27).

### Result

| Field | n | Omnibus T | Null mean (p95) | p | q (BH, 2 fields) |
|---|---:|---:|---|---:|---:|
| notesaroma | 32 | 19.84 | 9.66 (18.26) | 0.031 | 0.062 |
| flavor_notes | 33 | 8.36 | 9.65 (18.57) | 0.543 | 0.543 |

Per family, difference in endorsement rate (stimulation - sham) with its 95% CI, p and q; the larger or nominally significant ones, all are in `outputs/family_endorsement_report.md`:

| Field | Family | Stimulation | Sham | Difference [95% CI] | p | q (BH, 18 tests) |
|---|---|---:|---:|---|---:|---:|
| notesaroma | sweet | 0.22 | 0.14 | +0.08 [+0.01, +0.15] | 0.040 | 0.32 |
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | 0.040 | 0.32 |
| notesaroma | green/vegetative | 0.07 | 0.13 | -0.06 [-0.12, -0.00] | 0.071 | 0.32 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.05 [-0.00, +0.11] | 0.100 | 0.36 |
| flavor_notes | roasted | 0.29 | 0.21 | +0.08 [-0.00, +0.16] | 0.067 | 0.32 |

Wheel family 5 (chemical, papery/musty) is endorsed at 0.03 / 0.03 (aroma) and 0.08 / 0.08 (flavor); `unmapped` at 0.03 / 0.05 and 0.04 / 0.05. Tasting interaction: aroma sum F = 2.8 (null mean 9.3), p = 0.998; flavor sum F = 11.4 (null mean 9.4), p = 0.23, so there is no evidence that the condition effect differs between tastings.

Reading: for aroma, the families differ overall at a nominal level (p = 0.031), with stimulation higher on sweet and lower on floral and green/vegetative, but the omnibus does not survive FDR over the two fields (q = 0.062), no single family reaches q below 0.3, and the intervals are wide. Flavor shows no difference. With 32 to 33 participants and at most six tastings per condition, only differences of roughly 0.15 or more in endorsement rate can be detected reliably, so this is "no clear evidence", not evidence of equal profiles.

## Secondary: Jensen-Shannon distance between pooled distributions

Compares pooled counts, so participants who wrote more weigh more, it cannot say which families differ, and it is blind to a change in how many families are endorsed. Kept as a descriptive summary; the endorsement analysis above is the one to report. `python3 distribution/jsd_by_level.py` (10000 swaps).

- Counts: per field and condition, each descriptor adds one count to every node it contains, rolled up to the level (1 = family, 9 wheel families plus `unmapped`; 2 = category; 3 = term). A node mapped coarser than the level ("fruit" is a family; `unmapped` has no category) is unresolved there and left out; the counts kept are in the table.
- Statistic: Jensen-Shannon distance (sqrt of the base-2 divergence; 0 = identical, 1 = no shared nodes) between the pooled stimulation and sham distributions.
- Reference: sparse counts bias the distance upward (more nodes, larger bias), so it is judged against a paired permutation null (each participant's stimulation and sham descriptors swapped with probability 1/2); p is the share of swaps with a distance at least as large, and the excess over the null mean is reported. BH-FDR over the 6 tests (3 levels x 2 fields).

| Field | Level | Nodes | Counts (stim / sham) | JS distance | Null mean | Excess | p | q (BH) |
|---|---|---:|---|---:|---:|---:|---:|---:|
| notesaroma | 1 family | 10 | 298 / 296 | 0.133 | 0.099 | +0.035 | 0.073 | 0.16 |
| notesaroma | 2 category | 24 | 314 / 309 | 0.196 | 0.167 | +0.029 | 0.078 | 0.16 |
| notesaroma | 3 term | 58 | 231 / 210 | 0.331 | 0.320 | +0.011 | 0.317 | 0.46 |
| flavor_notes | 1 family | 10 | 352 / 316 | 0.069 | 0.079 | -0.010 | 0.672 | 0.67 |
| flavor_notes | 2 category | 23 | 367 / 342 | 0.152 | 0.147 | +0.005 | 0.381 | 0.46 |
| flavor_notes | 3 term | 56 | 260 / 250 | 0.339 | 0.307 | +0.032 | 0.077 | 0.16 |

No level survives FDR (smallest q = 0.16). The nominal family-level `notesaroma` excess (p = 0.073) is smaller than before `unmapped` was separated from wheel family 5 (it was p = 0.048 when the two were pooled), which shows how sensitive these pooled distances are to a single category definition.

### By tasting (family level)

`python3 distribution/jsd_by_level.py --levels 1 --stratify repeated_ratings`: the same analysis within each repeated tasting (the coffee cools from tasting 1 to 3), swap test within each tasting, BH-FDR over the 6 tests. Counts are about 90 to 130 per condition, so the excess over the null is the informative column.

| Field | Tasting | Counts (stim / sham) | JS distance | Null mean | Excess | p | q (BH, 6 tests) |
|---|---:|---|---:|---:|---:|---:|---:|
| notesaroma | 1 | 117 / 111 | 0.141 | 0.131 | +0.010 | 0.387 | 0.58 |
| notesaroma | 2 | 95 / 94 | 0.191 | 0.169 | +0.023 | 0.292 | 0.58 |
| notesaroma | 3 | 86 / 91 | 0.212 | 0.162 | +0.049 | 0.106 | 0.58 |
| flavor_notes | 1 | 130 / 109 | 0.163 | 0.140 | +0.023 | 0.247 | 0.58 |
| flavor_notes | 2 | 101 / 102 | 0.109 | 0.139 | -0.030 | 0.800 | 0.80 |
| flavor_notes | 3 | 121 / 105 | 0.115 | 0.127 | -0.012 | 0.632 | 0.76 |

No tasting shows a family-level difference (smallest q = 0.58).

### Cosine mapping (sensitivity)

`python3 distribution/validate_cosine_mapping.py` checks how well cosine similarity to category prototypes (Qwen, aroma/flavor instruction) recovers the manual mapping; `python3 distribution/jsd_by_level.py --mapping cosine` re-runs the analysis with it. The prototype of a category is the mean embedding of its family name, its own name and its level-3 terms. The ten words with no wheel home (butter, cream, ripe, plane, milk, rusty, peppermint, cookie, iron, fat) are set to `unmapped` by hand in `data/sca_aliases.csv`, so no threshold is needed. Exact wheel terms are unchanged; the other alias words are re-assigned to the nearest category, the family is that category's parent, and since they are resolved to a category only they are left out at level 3.

Agreement with the manual mapping (all 109 mapped units; weighted by occurrences in brackets): category 0.71 (0.86), family 0.82 (0.93). Aliases alone: category 0.73 (0.93), family 0.83 (0.96). Disagreements are mostly arguable (smoky as tobacco vs burnt, cherry and grape as berry, prune as other fruit, nutmeg as nutty), plus a few real mistakes (citric to citrus, raisin to cereal, bean to cereal). Full table: `outputs/cosine_mapping_validation.md`.

Result with cosine mapping (`outputs/jsd_by_level_cosine.csv`; the manual result in brackets):

| Field | Level | JS distance | Excess | p | q (BH) |
|---|---|---:|---:|---:|---:|
| notesaroma | 1 family | 0.134 (0.133) | +0.035 (+0.035) | 0.065 (0.073) | 0.39 (0.16) |
| notesaroma | 2 category | 0.171 (0.196) | +0.011 (+0.029) | 0.272 (0.078) | 0.49 (0.16) |
| notesaroma | 3 term | 0.326 (0.331) | +0.011 (+0.011) | 0.325 (0.317) | 0.49 (0.46) |
| flavor_notes | 1 family | 0.074 (0.069) | -0.004 (-0.010) | 0.561 (0.672) | 0.56 (0.67) |
| flavor_notes | 2 category | 0.139 (0.152) | +0.002 (+0.005) | 0.458 (0.381) | 0.55 (0.46) |
| flavor_notes | 3 term | 0.316 (0.339) | +0.022 (+0.032) | 0.161 (0.077) | 0.48 (0.16) |

The conclusion does not depend on the mapping: nothing survives FDR.

## Caveats

- The wheel mapping and the alias file were written after viewing the data, so the analysis is exploratory.
- Endorsement rates are computed per participant over all usable tastings; participants with more missing tastings are noisier and are not weighted differently.
- In the Jensen-Shannon analyses counts pool descriptors across participants, so participants who wrote more descriptors weigh more; a descriptor with two words in the same family counts once at level 1.
