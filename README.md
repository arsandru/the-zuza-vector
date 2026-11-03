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

## Stimulation vs sham (exploratory)

`python3 irr/compare_conditions.py` tests delta = kappa(stimulation) - kappa(sham) per field, same pipeline and model. All 34 participants contribute to both conditions, so the CI is a paired participant bootstrap (2000) and the p-value a permutation test that swaps each participant's stimulation and sham descriptor sets (2000). Holm over the two fields. Output: `irr/outputs/condition_comparison.csv`.

| Field | Stimulation | Sham | Delta [95% CI] | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| notesaroma | 0.052 | 0.050 | +0.002 [-0.025, 0.032] | 0.88 | 1.0 |
| flavor_notes | 0.046 | 0.051 | -0.005 [-0.035, 0.025] | 0.74 | 1.0 |

No evidence of a difference in between-participant agreement; the intervals are about +/-0.03 around zero, against kappas of about 0.05.

### Does cleaning or the model drive it?

`python3 irr/cleaning_sensitivity.py` repeats the comparison with each cleaning step on or off (raw, spelling only, lemma only, stop words only, synonym variants only, lemma + stop words, full) under Qwen, and with raw and full cleaning under bge-small and all-mpnet. Table: `irr/outputs/cleaning_sensitivity.md`. In all 22 runs the difference is between -0.006 and +0.006 and every interval includes zero (p from 0.33 to 1.00). The sign of the `notesaroma` difference flips between runs (raw Qwen -0.001, full Qwen +0.002, mpnet +0.003 to +0.004) at a size far below its interval of about +/-0.03, so the apparent reversal is noise around zero, not an effect of the cleaning. Cleaning does not change kappa within Qwen (0.048 to 0.053 for `notesaroma`); the model does (bge and mpnet about 0.02 to 0.03).

## Caveats

- The flavour notes are the second text column, whose header in the file is `bitter, roasted`; it is called `flavor_notes` here.
- Chance shuffles each participant's descriptors across the 6 items, so it keeps their vocabulary and removes item-specific agreement. Items are not split into coffee and repeat.
- The spelling fixes, synonym variants and filler stop words were listed after viewing the data, so the cleaning is exploratory.
- `data/tDCS.csv` is participant data and is committed locally; decide before adding a remote.
