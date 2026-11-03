# the-zuza-vector

Between-participant semantic agreement (IRR) on the free-text coffee descriptors of the tDCS study (`data/tDCS.csv`), analysed within each condition (stimulation, sham). Exploratory and descriptive.

Repurposed from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py`: three fixed raters over clusters became 34 participants over 6 items (coffee x repeated tasting).

## Run

From the repository root: `python3 irr/semantic_irr.py` (defaults: 2000 permutations, 1000 bootstraps, seed 42). Needs `requirements.txt` and the spaCy model (`python3 -m spacy download en_core_web_sm`). Embeddings: Qwen3-Embedding-0.6B with the instruction `Instruct: Embed aroma/flavor descriptors.` Each descriptor is cleaned first: spelling standardisation, spaCy lemmatisation, stop-word removal (negation and degree words kept, tasting-note filler such as "aroma" and "taste" dropped), then standardisation of synonym variants (burned/burnt, chocolaty/chocolate, and so on). The raw to cleaned map is in `irr/outputs/cleaned_descriptors.csv`. Outputs go to `irr/outputs/`. The docstring of the script defines the method.

## Result (default settings, semantic kappa [95% participant-bootstrap CI])

| Field | Stimulation | Sham |
|---|---|---|
| notesaroma | 0.052 [0.026, 0.081] | 0.050 [0.029, 0.074] |
| flavor_notes | 0.046 [0.026, 0.072] | 0.052 [0.026, 0.083] |

Agreement is above chance but very low: participants' descriptors are barely closer to each other for the same sample than for different samples. Thresholded versions are in `irr/outputs/semantic_irr_report.md`. The earlier run with bge-small and all-mpnet (no cleaning beyond crude lemmatisation) gave 0.016 to 0.029; the scale of kappa depends on the embedding, so compare across conditions and fields within one model.

## Caveats

- The flavour notes are the second text column, whose header in the file is `bitter, roasted`; it is called `flavor_notes` here.
- Chance shuffles each participant's descriptors across the 6 items, so it keeps their vocabulary and removes item-specific agreement. Items are not split into coffee and repeat.
- The spelling fixes, synonym variants and filler stop words were listed after viewing the data, so the cleaning is exploratory.
- The stimulation vs sham difference in agreement is not tested.
- `data/tDCS.csv` is participant data and is committed locally; decide before adding a remote.
