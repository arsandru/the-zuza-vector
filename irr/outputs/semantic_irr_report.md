# Between-participant semantic agreement within condition (descriptive)

- Input: `tDCS.csv`; 34 participants; items = coffee x repeated tasting (6 per condition).
- Rater = participant; each condition and text field analysed separately. Chance = each participant's descriptors shuffled across items (n = 2000); CI = participant bootstrap (n = 1000, expected similarity recomputed with 100 shuffles).
- Cleaning (rules written after viewing the data): lowercase, 33 spelling fixes, spaCy lemmatisation, stop-word removal, lemma standardisation (see script constants); model Qwen/Qwen3-Embedding-0.6B with instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'. Seed 42.
- Stimulation vs sham: see compare_conditions.py (condition_comparison.csv).

| Model | Field | Condition | Participants | Descriptors | Pairs | Observed | Expected | Semantic kappa | 95% CI | kappa t=0.60 | kappa t=0.70 | kappa t=0.80 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-Embedding-0.6B | notesaroma | stimulation | 34 | 183 | 2704 | 0.678 | 0.655 | 0.068 | [0.037, 0.104] | 0.277 | 0.127 | 0.039 |
| Qwen3-Embedding-0.6B | notesaroma | sham | 34 | 178 | 2556 | 0.678 | 0.655 | 0.068 | [0.041, 0.097] | 0.257 | 0.141 | 0.042 |
| Qwen3-Embedding-0.6B | flavor_notes | stimulation | 34 | 184 | 2735 | 0.666 | 0.646 | 0.057 | [0.033, 0.086] | 0.227 | 0.093 | 0.023 |
| Qwen3-Embedding-0.6B | flavor_notes | sham | 34 | 182 | 2679 | 0.668 | 0.646 | 0.063 | [0.033, 0.096] | 0.240 | 0.098 | 0.037 |
