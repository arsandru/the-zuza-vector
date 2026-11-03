# Between-participant semantic agreement within condition (descriptive)

- Input: `tDCS.csv`; 34 participants; items = coffee x repeated tasting (6 per condition).
- Rater = participant; each condition and text field analysed separately. Chance = each participant's descriptors shuffled across items (n = 2000); CI = participant bootstrap (n = 1000, expected similarity recomputed with 100 shuffles).
- Cleaning: lowercase, 23 misspelling fixes (written after viewing the data), stop-word removal, crude lemmatisation. Seed 42.
- Not tested: the stimulation vs sham difference.

| Model | Field | Condition | Participants | Descriptors | Pairs | Observed | Expected | Semantic kappa | 95% CI | kappa t=0.60 | kappa t=0.70 | kappa t=0.80 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bge-small-en-v1.5 | notesaroma | stimulation | 34 | 204 | 3366 | 0.612 | 0.603 | 0.024 | [0.010, 0.040] | 0.091 | 0.043 | 0.006 |
| bge-small-en-v1.5 | notesaroma | sham | 34 | 204 | 3366 | 0.609 | 0.599 | 0.025 | [0.010, 0.040] | 0.081 | 0.042 | 0.009 |
| bge-small-en-v1.5 | flavor_notes | stimulation | 34 | 200 | 3234 | 0.616 | 0.609 | 0.018 | [0.008, 0.030] | 0.061 | 0.024 | 0.010 |
| bge-small-en-v1.5 | flavor_notes | sham | 34 | 199 | 3204 | 0.607 | 0.601 | 0.016 | [0.004, 0.029] | 0.055 | 0.027 | 0.010 |
| all-mpnet-base-v2 | notesaroma | stimulation | 34 | 204 | 3366 | 0.351 | 0.331 | 0.029 | [0.014, 0.047] | 0.026 | 0.009 | 0.003 |
| all-mpnet-base-v2 | notesaroma | sham | 34 | 204 | 3366 | 0.333 | 0.316 | 0.025 | [0.011, 0.039] | 0.021 | 0.008 | 0.002 |
| all-mpnet-base-v2 | flavor_notes | stimulation | 34 | 200 | 3234 | 0.349 | 0.334 | 0.023 | [0.012, 0.036] | 0.017 | 0.007 | 0.003 |
| all-mpnet-base-v2 | flavor_notes | sham | 34 | 199 | 3204 | 0.352 | 0.336 | 0.024 | [0.008, 0.040] | 0.021 | 0.010 | 0.003 |
