# Between-participant semantic agreement within condition (descriptive)

- Input: `tDCS.csv`; 34 participants; items = coffee x repeated tasting (6 per condition).
- Rater = participant; each condition and text field analysed separately. Chance = each participant's descriptors shuffled across items (n = 2000); CI = participant bootstrap (n = 1000, expected similarity recomputed with 100 shuffles).
- Cleaning (rules written after viewing the data): lowercase, 33 spelling fixes, spaCy lemmatisation, stop-word removal, lemma standardisation (see script constants); model Qwen/Qwen3-Embedding-0.6B with instruction 'Instruct: Embed aroma/flavor descriptors.\nText:'. Seed 42.
- Stimulation vs sham: see compare_conditions.py (condition_comparison.csv).

| Model | Field | Condition | Participants | Descriptors | Pairs | Observed | Expected | Semantic kappa | 95% CI | kappa t=0.60 | kappa t=0.70 | kappa t=0.80 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-Embedding-0.6B | notesaroma | stimulation | 34 | 188 | 2853 | 0.670 | 0.648 | 0.062 | [0.033, 0.093] | 0.228 | 0.115 | 0.035 |
| Qwen3-Embedding-0.6B | notesaroma | sham | 34 | 179 | 2586 | 0.673 | 0.650 | 0.066 | [0.040, 0.092] | 0.246 | 0.130 | 0.039 |
| Qwen3-Embedding-0.6B | flavor_notes | stimulation | 34 | 188 | 2855 | 0.658 | 0.639 | 0.052 | [0.030, 0.080] | 0.210 | 0.083 | 0.019 |
| Qwen3-Embedding-0.6B | flavor_notes | sham | 34 | 185 | 2766 | 0.663 | 0.642 | 0.060 | [0.031, 0.093] | 0.230 | 0.092 | 0.033 |
