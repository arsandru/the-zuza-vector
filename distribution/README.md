# distribution: do stimulation and sham endorse different wheel-family profiles? (exploratory)

Descriptors are cleaned (main pipeline of `irr/`) and mapped to the SCA flavor wheel (`wheel_mapping.py`, `data/SCA flavor wheel.csv`, `data/sca_aliases.csv`). Words with no wheel home (38 occurrences; the ten listed in the alias file as IGNORE, plus any other unmatched word) are left out of these analyses: a descriptor is judged on its remaining words, and one with none left is missing. Wheel family 5 (`5_other`: chemical, papery/musty) only receives words that really map there. Multiplicity: Benjamini-Hochberg FDR (q) within each family of tests.

## Main analysis: family endorsement (`family_endorsement.py`)

Run from the repository root: `python3 distribution/family_endorsement.py` (10000 sign-flip permutations and bootstrap draws, seed 42). The docstring defines the method.

Check-all-that-apply design: at each tasting (2 coffees x 3 repeated tastings per condition) a participant endorses a wheel family if any word of the descriptor maps to it; a tasting without a usable descriptor ("n\\a", or no word that maps to the wheel) is missing, not "not endorsed". The unit is the participant: endorsement rate = endorsed / non-missing tastings, per condition, field and family; paired difference d = stimulation - sham, with participants who have no usable tasting in a condition left out of that field (aroma n = 32, flavor n = 33).

1. Omnibus per field: T = sum over the 9 wheel families of the squared paired t, judged against a paired sign-flip permutation (each participant's stimulation and sham labels swapped with probability 1/2). BH-FDR q over the 2 fields.
2. Per family: mean difference in endorsement rate with a participant-bootstrap 95% CI, unadjusted sign-flip p, and BH-FDR q over the 2 x 9 family tests.
3. Does the condition effect vary across the 3 tastings? Sum over families of the repeated-measures F of the per-tasting difference, null from permuting tasting labels within participant (participants with all three tastings usable: aroma 30, flavor 27).

### Result

Figure: `outputs/distribution_plot.pdf` and `.png` (`python3 distribution/plot_distribution.py`), a descriptive radar plot: the 9 wheel families are the axes (wheel order, clockwise from floral), each condition is a polygon whose radius is the mean endorsement rate of the family (stimulation red, sham blue), aroma notes left and flavor notes right. The caption reports the omnibus p and q (and the cosine-mapping q) and that no single family reaches q below 0.25, so differences between the polygons for individual families are not significant. Earlier versions of this figure (a forest plot of per-family differences with CIs, and a scatter of participants' words in flavor-wheel space) are in git history (`c3c6bcd`, `02547f1`); the forest plot's numbers are in `outputs/family_endorsement_report.md`.

| Field | n | Omnibus T | Null mean (p95) | p | q (BH, 2 fields) |
|---|---:|---:|---|---:|---:|
| notesaroma | 32 | 21.71 | 9.65 (18.49) | 0.018 | 0.035 |
| flavor_notes | 33 | 8.35 | 9.66 (18.50) | 0.542 | 0.542 |

Per family, difference in endorsement rate (stimulation - sham) with its 95% CI, p and q; the larger or nominally significant ones, all are in `outputs/family_endorsement_report.md`:

| Field | Family | Stimulation | Sham | Difference [95% CI] | p | q (BH, 18 tests) |
|---|---|---:|---:|---|---:|---:|
| notesaroma | sweet | 0.23 | 0.14 | +0.08 [+0.01, +0.15] | 0.041 | 0.25 |
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | 0.042 | 0.25 |
| notesaroma | green/vegetative | 0.07 | 0.14 | -0.07 [-0.13, -0.02] | 0.020 | 0.25 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.06 [+0.00, +0.12] | 0.081 | 0.29 |
| flavor_notes | roasted | 0.29 | 0.21 | +0.08 [-0.00, +0.16] | 0.074 | 0.29 |

Wheel family 5 is endorsed at 0.03 / 0.03 (aroma) and 0.08 / 0.08 (flavor), stimulation / sham. Tasting interaction: aroma sum F = 3.6 (null mean 9.3), p = 0.991; flavor sum F = 12.1 (null mean 9.4), p = 0.18, so there is no evidence that the condition effect differs between tastings.

Reading: for aroma, the family profiles differ overall (omnibus p = 0.018, q = 0.035), with stimulation higher on sweet and sour/fermented and lower on floral and green/vegetative; flavor shows no difference. The omnibus is spread over several families: no single family reaches q below 0.25 and the intervals are wide. The aroma omnibus is sensitive to how words with no wheel home are treated: when they were instead kept as a separate catch-all category (so that a descriptor of only such words counted as "endorsed nothing", commit `dce7381`) it was p = 0.031, q = 0.062. With 32 to 33 participants and at most six tastings per condition, only differences of roughly 0.15 or more in endorsement rate can be detected reliably for a single family.

### Cosine mapping (sensitivity of the main analysis)

`python3 distribution/family_endorsement.py --mapping cosine` repeats the analysis with the cosine mapping described below (alias words re-assigned to the nearest wheel category, family = its parent; exact wheel terms unchanged). Outputs carry the suffix `_cosine`.

| Mapping | Field | Omnibus T | p | q (BH, 2 fields) |
|---|---|---:|---:|---:|
| manual | notesaroma | 21.71 | 0.018 | 0.035 |
| cosine | notesaroma | 19.88 | 0.028 | 0.057 |
| manual | flavor_notes | 8.35 | 0.542 | 0.542 |
| cosine | flavor_notes | 9.82 | 0.418 | 0.418 |

The aroma pattern is the same under both mappings (stimulation higher on sweet, +0.08 in both, and sour/fermented; lower on floral and green/vegetative, -0.06 each) and no single family reaches q below 0.27, but the omnibus sits on either side of q = 0.05 depending on the mapping (0.035 manual, 0.057 cosine), so it is not robust to the mapping and should be reported as "suggestive for aroma, not robust". Flavor shows no difference under either. Tasting interaction: aroma p = 0.999; flavor p = 0.051 under the cosine mapping (0.18 under the manual one), a borderline result in one of four such tests that I would not interpret.

## Secondary: Jensen-Shannon distance between pooled distributions

Compares pooled counts, so participants who wrote more weigh more, it cannot say which families differ, and it is blind to a change in how many families are endorsed. Kept as a descriptive summary; the endorsement analysis above is the one to report. `python3 distribution/jsd_by_level.py` (10000 swaps).

- Counts: per field and condition, each descriptor adds one count to every node it contains, rolled up to the level (1 = the 9 wheel families; 2 = category; 3 = term). A node mapped coarser than the level ("fruit" is a family) is unresolved there and left out; the counts kept are in the table.
- Statistic: Jensen-Shannon distance (sqrt of the base-2 divergence; 0 = identical, 1 = no shared nodes) between the pooled stimulation and sham distributions.
- Reference: sparse counts bias the distance upward (more nodes, larger bias), so it is judged against a paired permutation null (each participant's stimulation and sham descriptors swapped with probability 1/2); p is the share of swaps with a distance at least as large, and the excess over the null mean is reported. BH-FDR over the 6 tests (3 levels x 2 fields).

| Field | Level | Nodes | Counts (stim / sham) | JS distance | Null mean | Excess | p | q (BH) |
|---|---|---:|---|---:|---:|---:|---:|---:|
| notesaroma | 1 family | 9 | 292 / 286 | 0.130 | 0.091 | +0.039 | 0.051 | 0.16 |
| notesaroma | 2 category | 24 | 314 / 309 | 0.196 | 0.167 | +0.029 | 0.078 | 0.16 |
| notesaroma | 3 term | 58 | 231 / 210 | 0.331 | 0.320 | +0.011 | 0.317 | 0.46 |
| flavor_notes | 1 family | 9 | 345 / 307 | 0.066 | 0.077 | -0.011 | 0.699 | 0.70 |
| flavor_notes | 2 category | 23 | 367 / 342 | 0.152 | 0.147 | +0.005 | 0.381 | 0.46 |
| flavor_notes | 3 term | 56 | 260 / 250 | 0.339 | 0.307 | +0.032 | 0.077 | 0.16 |

No level survives FDR (smallest q = 0.16); the family-level `notesaroma` excess is nominal (p = 0.051).

### By tasting (family level)

`python3 distribution/jsd_by_level.py --levels 1 --stratify repeated_ratings`: the same analysis within each repeated tasting (the coffee cools from tasting 1 to 3), swap test within each tasting, BH-FDR over the 6 tests. Counts are about 80 to 130 per condition, so the excess over the null is the informative column.

| Field | Tasting | Counts (stim / sham) | JS distance | Null mean | Excess | p | q (BH, 6 tests) |
|---|---:|---|---:|---:|---:|---:|---:|
| notesaroma | 1 | 116 / 106 | 0.101 | 0.124 | -0.023 | 0.734 | 0.84 |
| notesaroma | 2 | 95 / 91 | 0.144 | 0.143 | +0.001 | 0.486 | 0.84 |
| notesaroma | 3 | 81 / 89 | 0.200 | 0.156 | +0.045 | 0.132 | 0.48 |
| flavor_notes | 1 | 128 / 106 | 0.161 | 0.128 | +0.033 | 0.161 | 0.48 |
| flavor_notes | 2 | 99 / 98 | 0.099 | 0.133 | -0.034 | 0.843 | 0.84 |
| flavor_notes | 3 | 118 / 103 | 0.115 | 0.126 | -0.011 | 0.614 | 0.84 |

No tasting shows a family-level difference (smallest q = 0.48).

### Cosine mapping (sensitivity)

`python3 distribution/validate_cosine_mapping.py` checks how well cosine similarity to category prototypes (Qwen, aroma/flavor instruction) recovers the manual mapping; `python3 distribution/jsd_by_level.py --mapping cosine` re-runs the analysis with it. The prototype of a category is the mean embedding of its family name, its own name and its level-3 terms. Exact wheel terms are unchanged; the other alias words are re-assigned to the nearest category, the family is that category's parent, and since they are resolved to a category only they are left out at level 3.

Agreement with the manual mapping (all 109 mapped units; weighted by occurrences in brackets): category 0.71 (0.86), family 0.82 (0.93). Aliases alone: category 0.73 (0.93), family 0.83 (0.96). Disagreements are mostly arguable (smoky as tobacco vs burnt, cherry and grape as berry, prune as other fruit, nutmeg as nutty), plus a few real mistakes (citric to citrus, raisin to cereal, bean to cereal). Full table: `outputs/cosine_mapping_validation.md`.

Result with cosine mapping (`outputs/jsd_by_level_cosine.csv`; the manual result in brackets):

| Field | Level | JS distance | Excess | p | q (BH) |
|---|---|---:|---:|---:|---:|
| notesaroma | 1 family | 0.131 (0.130) | +0.040 (+0.039) | 0.044 (0.051) | 0.26 (0.16) |
| notesaroma | 2 category | 0.171 (0.196) | +0.011 (+0.029) | 0.272 (0.078) | 0.49 (0.16) |
| notesaroma | 3 term | 0.326 (0.331) | +0.011 (+0.011) | 0.325 (0.317) | 0.49 (0.46) |
| flavor_notes | 1 family | 0.071 (0.066) | -0.005 (-0.011) | 0.585 (0.699) | 0.59 (0.70) |
| flavor_notes | 2 category | 0.139 (0.152) | +0.002 (+0.005) | 0.458 (0.381) | 0.55 (0.46) |
| flavor_notes | 3 term | 0.316 (0.339) | +0.022 (+0.032) | 0.161 (0.077) | 0.48 (0.16) |

Nothing survives FDR under either mapping.

## Caveats

- The wheel mapping and the alias file were written after viewing the data, so the analysis is exploratory.
- Endorsement rates are computed per participant over all usable tastings; participants with more missing tastings are noisier and are not weighted differently.
- In the Jensen-Shannon analyses counts pool descriptors across participants, so participants who wrote more descriptors weigh more; a descriptor with two words in the same family counts once at level 1.
