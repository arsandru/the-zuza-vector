# the-zuza-vector

Between-participant semantic agreement (IRR) on the free-text coffee descriptors of the tDCS study (`data/tDCS.csv`), analysed within each condition (stimulation, sham). Exploratory and descriptive.

Repurposed from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py`: three fixed raters over clusters became 34 participants over 6 items (coffee x repeated tasting).

## Run

From the repository root: `python3 irr/semantic_irr.py` (defaults: 2000 permutations, 1000 bootstraps, seed 42). Needs `requirements.txt` and the spaCy model (`python3 -m spacy download en_core_web_sm`). Embeddings: Qwen3-Embedding-0.6B with the instruction `Instruct: Embed aroma/flavor descriptors.` Each descriptor is cleaned first: spelling standardisation, spaCy lemmatisation, stop-word removal (negation and degree words kept, tasting-note filler such as "aroma" and "taste" dropped), then standardisation of synonym variants (burned/burnt, chocolaty/chocolate, and so on). The raw to cleaned map is in `irr/outputs/cleaned_descriptors.csv`. Outputs go to `irr/outputs/`. The docstring of the script defines the method.

## Result (default settings, semantic kappa [95% participant-bootstrap CI])

| Field | Stimulation | Sham |
|---|---|---|
| notesaroma | 0.062 [0.033, 0.093] | 0.066 [0.040, 0.092] |
| flavor_notes | 0.052 [0.030, 0.080] | 0.060 [0.031, 0.093] |

Agreement is above chance but very low: participants' descriptors are barely closer to each other for the same sample than for different samples. Thresholded versions are in `irr/outputs/semantic_irr_report.md`. The scale of kappa depends on the embedding (bge-small and all-mpnet give about 0.02 to 0.04), so compare across conditions and fields within one model. "n\\a" (not available) answers are treated as missing, not as a descriptor (see Corrections).

## Stimulation vs sham (exploratory)

`python3 irr/compare_conditions.py` tests delta = kappa(stimulation) - kappa(sham) per field, same pipeline and model. All 34 participants contribute to both conditions, so the CI is a paired participant bootstrap (2000) and the p-value a permutation test that swaps each participant's stimulation and sham descriptor sets (2000). Holm over the two fields. Output: `irr/outputs/condition_comparison.csv`.

| Field | Stimulation | Sham | Delta [95% CI] | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| notesaroma | 0.062 | 0.065 | -0.003 [-0.035, 0.032] | 0.86 | 1.0 |
| flavor_notes | 0.052 | 0.060 | -0.008 [-0.040, 0.023] | 0.60 | 1.0 |

No evidence of a difference in between-participant agreement; the intervals are about +/-0.03 around zero, against kappas of about 0.06.

### Does cleaning or the model drive it?

`python3 irr/cleaning_sensitivity.py` repeats the comparison with each cleaning step on or off (raw, spelling only, lemma only, stop words only, synonym variants only, lemma + stop words, full), with a "descriptors only" variant that also drops words that are not aroma or flavor descriptors (comparison, intensity, evaluation and mouthfeel words such as more, less, strong, thinner, better, bad, watery; a descriptor left empty becomes missing), and with raw, full and descriptors-only cleaning under bge-small and all-mpnet. Table: `irr/outputs/cleaning_sensitivity.md`. In every run the stimulation vs sham difference is within about +/-0.01 and every interval includes zero; its sign changes between runs, so it is noise around zero. Cleaning changes kappa little within a model (Qwen `notesaroma`: 0.059 to 0.068); descriptors only raises it slightly (0.068 and 0.068 for `notesaroma`, 0.057 and 0.063 for `flavor_notes`), so non-descriptor words added a little noise but did not create or hide a condition difference. The model changes the scale (bge and mpnet about 0.03 to 0.04).

## Corrections

- A first version embedded the 67 "n\a" non-responses (41 in `notesaroma`, 26 in `flavor_notes`) as if they were a descriptor, so they counted as perfect agreement between participants. They are now missing. All kappas and comparisons above come from the corrected run; earlier numbers (kappa about 0.05, differences +0.002 and -0.005) were from the uncorrected version.
- Cleaned descriptors that consist only of stop words (for example "same as before") still fall back to their raw text in the default pipeline; the descriptors-only variant makes them missing.

## Caveats

- The flavour notes are the second text column, whose header in the file is `bitter, roasted`; it is called `flavor_notes` here.
- Chance shuffles each participant's descriptors across the 6 items, so it keeps their vocabulary and removes item-specific agreement. Items are not split into coffee and repeat.
- The spelling fixes, synonym variants and filler stop words were listed after viewing the data, so the cleaning is exploratory.
- `data/tDCS.csv` is participant data and is committed locally; decide before adding a remote.
