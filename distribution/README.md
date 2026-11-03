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

## Caveats

- The wheel mapping and the alias file were written after viewing the data, so the analysis is exploratory. Unmapped words are in `5_other`, which is a real wheel family as well (chemical, papery/musty), so level 1 mixes them.
- Counts pool descriptors across participants, so participants who wrote more descriptors weigh more; the swap test keeps this structure.
- Descriptors, not participants, are counted, and a descriptor with two words in the same family counts once at level 1.
