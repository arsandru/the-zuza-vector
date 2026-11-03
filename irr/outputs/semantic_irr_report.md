# Between-participant semantic agreement within condition (descriptive)

- Input: `tDCS.csv`; 34 participants; items = coffee x repeated tasting (6 per condition).
- Rater = participant; each condition and text field analysed separately. Chance = each participant's descriptors shuffled across items (n = 2000); CI = participant bootstrap (n = 1000, expected similarity recomputed with 100 shuffles).
- Cleaning (rules written after viewing the data): lowercase, 33 spelling fixes, spaCy lemmatisation, stop-word removal, lemma standardisation (see script constants); model Qwen/Qwen3-Embedding-0.6B with instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'. Seed 42.
- Not tested: the stimulation vs sham difference.

| Model | Field | Condition | Participants | Descriptors | Pairs | Observed | Expected | Semantic kappa | 95% CI | kappa t=0.60 | kappa t=0.70 | kappa t=0.80 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-Embedding-0.6B | notesaroma | stimulation | 34 | 204 | 3366 | 0.664 | 0.645 | 0.052 | [0.026, 0.081] | 0.205 | 0.092 | 0.029 |
| Qwen3-Embedding-0.6B | notesaroma | sham | 34 | 204 | 3366 | 0.665 | 0.648 | 0.050 | [0.029, 0.074] | 0.194 | 0.094 | 0.031 |
| Qwen3-Embedding-0.6B | flavor_notes | stimulation | 34 | 200 | 3234 | 0.654 | 0.637 | 0.046 | [0.026, 0.072] | 0.197 | 0.071 | 0.017 |
| Qwen3-Embedding-0.6B | flavor_notes | sham | 34 | 199 | 3204 | 0.658 | 0.639 | 0.052 | [0.026, 0.083] | 0.209 | 0.075 | 0.028 |
