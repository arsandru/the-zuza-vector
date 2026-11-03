# distribution: stimulation vs sham wheel-node distributions (exploratory)

Does the mix of aroma and flavor descriptors differ between stimulation and sham? Descriptors are cleaned (main pipeline of `irr/`) and mapped to the SCA flavor wheel (`wheel_mapping.py`, `data/SCA flavor wheel.csv`, `data/sca_aliases.csv`); the distributions of wheel nodes are compared at each level with the Jensen-Shannon distance.

Run from the repository root: `python3 distribution/jsd_by_level.py` (10000 swaps, seed 42). The docstring defines the method.

## Method in short

- Counts: per text field and condition, each descriptor adds one count to every node it contains, rolled up to the level (1 = family, 9 nodes; 2 = category; 3 = term). A node mapped coarser than the level ("fruit" is a family; `5_other` has no category) is unresolved there and left out of that level; the counts kept are in the table.
- Statistic: Jensen-Shannon distance (sqrt of the base-2 divergence; 0 = identical, 1 = no shared nodes) between the pooled stimulation and sham distributions.
- Reference: sparse counts bias the distance upward (more nodes, larger bias), so it is judged against a paired permutation null in which each participant's stimulation and sham descriptors are swapped with probability 1/2. p is the share of swaps with a distance at least as large; the excess over the null mean is reported. Holm over the 6 tests (3 levels x 2 fields).

## Result

| Field | Level | Nodes | Counts (stim / sham) | JS distance | Null mean (p95) | Excess | p | Holm p |
|---|---|---:|---|---:|---|---:|---:|---:|
| notesaroma | 1 family | 9 | 298 / 295 | 0.129 | 0.089 (0.128) | +0.040 | 0.048 | 0.29 |
| notesaroma | 2 category | 24 | 314 / 309 | 0.196 | 0.167 (0.201) | +0.029 | 0.078 | 0.38 |
| notesaroma | 3 term | 58 | 231 / 210 | 0.331 | 0.320 (0.360) | +0.011 | 0.32 | 0.95 |
| flavor_notes | 1 family | 9 | 352 / 314 | 0.062 | 0.075 (0.110) | -0.012 | 0.73 | 0.95 |
| flavor_notes | 2 category | 23 | 367 / 342 | 0.152 | 0.147 (0.177) | +0.005 | 0.38 | 0.95 |
| flavor_notes | 3 term | 56 | 260 / 250 | 0.339 | 0.307 (0.344) | +0.032 | 0.077 | 0.38 |

Reading: no distribution difference survives correction. The one nominal result is `notesaroma` at the family level (p = 0.048, Holm 0.29), where sham has more floral (8.1% vs 4.4% of descriptors) and green/vegetative (8.1% vs 4.4%), and stimulation more sweet (13.1% vs 8.5%); this is one test of six and is descriptive. Raw distances rise with the number of nodes mostly through the sparse-count bias (the null mean rises with them), which is why the excess, not the raw distance, is the comparison across levels. Every node's counts, proportions and contribution to the divergence are in `outputs/jsd_node_proportions.csv`.

## Family level by tasting (repeated_ratings)

`python3 distribution/jsd_by_level.py --levels 1 --stratify repeated_ratings` repeats the family-level analysis separately within each repeated tasting (1, 2, 3; the coffee cools from tasting 1 to 3), with the swap test acting within each tasting; Holm over the 6 tests. Output: `outputs/jsd_by_level_by_repeated_ratings_levels1.csv` and `jsd_node_proportions_by_repeated_ratings_levels1.csv`. Counts per tasting are about 90 to 130 per condition, so the distance is dominated by the sparse-count bias and only the excess over the null is informative.

| Field | Tasting | Counts (stim / sham) | JS distance | Null mean (p95) | Excess | p | Holm p |
|---|---:|---|---:|---|---:|---:|---:|
| notesaroma | 1 | 117 / 110 | 0.106 | 0.117 (0.165) | -0.011 | 0.65 | 1.0 |
| notesaroma | 2 | 95 / 94 | 0.149 | 0.144 (0.214) | +0.005 | 0.43 | 1.0 |
| notesaroma | 3 | 86 / 91 | 0.200 | 0.149 (0.212) | +0.051 | 0.086 | 0.52 |
| flavor_notes | 1 | 130 / 108 | 0.160 | 0.129 (0.185) | +0.031 | 0.17 | 0.86 |
| flavor_notes | 2 | 101 / 101 | 0.095 | 0.132 (0.192) | -0.037 | 0.86 | 1.0 |
| flavor_notes | 3 | 121 / 105 | 0.114 | 0.122 (0.176) | -0.009 | 0.59 | 1.0 |

No tasting shows a family-level difference after correction. The largest excess is `notesaroma` at tasting 3 (p = 0.086, Holm 0.52): stimulation has more sour/fermented descriptors (11.6% vs 4.4%) and sham more floral (9.9% vs 3.5%) and green/vegetative (8.8% vs 3.5%); the counts are small (10 vs 4, 3 vs 9, 3 vs 8), so this is descriptive. The unstratified family result (p = 0.048 for `notesaroma`, Holm 0.29) comes mostly from tasting 3 (excess +0.051; tastings 1 and 2: -0.011 and +0.005), which is itself not significant, so it is weak evidence at best.

## Cosine mapping (sensitivity)

`python3 distribution/validate_cosine_mapping.py` checks how well cosine similarity to category prototypes (Qwen, aroma/flavor instruction) recovers the manual mapping; `python3 distribution/jsd_by_level.py --mapping cosine` re-runs the analysis with it. The prototype of a category is the mean embedding of its family name, its own name and its level-3 terms. The ten words with no wheel home (butter, cream, ripe, plane, milk, rusty, peppermint, cookie, iron, fat) are set to `5_other` by hand in `data/sca_aliases.csv`, so no threshold is needed. Exact wheel terms are unchanged; the other alias words are re-assigned to the nearest category, the family is that category's parent, and since they are resolved to a category only they are left out at level 3.

Agreement with the manual mapping (all 109 mapped units; weighted by occurrences in brackets): category 0.71 (0.86), family 0.82 (0.93). Aliases alone: category 0.73 (0.93), family 0.83 (0.96). Adding the family name to the prototype changes little (category weighted 0.84 -> 0.86). Disagreements are mostly arguable (smoky as tobacco vs burnt, cherry and grape as berry, prune as other fruit, nutmeg as nutty), plus a few real mistakes (citric to citrus, raisin to cereal, bean to cereal). Full table: `outputs/cosine_mapping_validation.md`.

Result with cosine mapping (`outputs/jsd_by_level_cosine.csv`; the manual result in brackets):

| Field | Level | JS distance | Excess | p | Holm p |
|---|---|---:|---:|---:|---:|
| notesaroma | 1 family | 0.128 (0.129) | +0.038 (+0.040) | 0.052 (0.048) | 0.31 (0.29) |
| notesaroma | 2 category | 0.171 (0.196) | +0.011 (+0.029) | 0.27 (0.078) | 1.0 (0.38) |
| notesaroma | 3 term | 0.326 (0.331) | +0.011 (+0.011) | 0.33 (0.32) | 1.0 (0.95) |
| flavor_notes | 1 family | 0.067 (0.062) | -0.008 (-0.012) | 0.63 (0.73) | 1.0 (0.95) |
| flavor_notes | 2 category | 0.139 (0.152) | +0.002 (+0.005) | 0.46 (0.38) | 1.0 (0.95) |
| flavor_notes | 3 term | 0.316 (0.339) | +0.022 (+0.032) | 0.16 (0.077) | 0.81 (0.38) |

The conclusion does not depend on the mapping: no difference survives correction. The nominal family-level `notesaroma` result is borderline under both (p = 0.052 and 0.048), and the category-level trend in the manual mapping (p = 0.078) goes away with cosine mapping.

## Caveats

- The wheel mapping and the alias file were written after viewing the data, so the analysis is exploratory. Unmapped words are in `5_other`, which is a real wheel family as well (chemical, papery/musty), so level 1 mixes them.
- Counts pool descriptors across participants, so participants who wrote more descriptors weigh more; the swap test keeps this structure.
- Descriptors, not participants, are counted, and a descriptor with two words in the same family counts once at level 1.
