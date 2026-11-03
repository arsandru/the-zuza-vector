# the-zuza-vector

Between-participant semantic agreement (IRR) on the free-text coffee descriptors of the tDCS study (`data/tDCS.csv`), analysed within each condition (stimulation, sham). Exploratory and descriptive.

Repurposed from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py`: three fixed raters over clusters became 34 participants over 6 items (coffee x repeated tasting).

## Run

From the repository root: `python3 irr/semantic_irr.py` (defaults: 2000 permutations, 1000 bootstraps, seed 42; needs `requirements.txt`, downloads two sentence-embedding models on first use). Outputs go to `irr/outputs/` (summary csv, per-item csv, report md). The docstring of the script defines the method.

## Result (default settings, kappa [95% participant-bootstrap CI])

| Field | Stimulation | Sham |
|---|---|---|
| notesaroma (bge-small) | 0.024 [0.010, 0.040] | 0.025 [0.010, 0.040] |
| second text column (bge-small) | 0.018 [0.008, 0.030] | 0.016 [0.004, 0.029] |

The second model (all-mpnet-base-v2) gives 0.023 to 0.029. Agreement is above chance but very low: the participants' descriptors are barely closer to each other for the same sample than for different samples. Full table with thresholded versions in `irr/outputs/semantic_irr_report.md`.

## Caveats

- The second text column has the header `bitter, roasted` in the file; it is treated as a second free-text field (`notes_second`). Confirm what it holds.
- Chance shuffles each participant's descriptors across the 6 items, so it keeps their vocabulary and removes item-specific agreement. Items are not split into coffee and repeat.
- Misspellings (24 fixes) were listed after viewing the data.
- The stimulation vs sham difference in agreement is not tested.
- `data/tDCS.csv` is participant data and is committed locally; decide before adding a remote.
