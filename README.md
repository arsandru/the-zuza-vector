# the-zuza-vector

Between-participant semantic agreement (IRR) on the free-text coffee descriptors of the tDCS study (`data/tDCS.csv`), analysed within each condition (stimulation, sham). Exploratory and descriptive.

Repurposed from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py`: three fixed raters over clusters became 34 participants over 6 items (coffee x repeated tasting).

## Run

From the repository root: `python3 irr/semantic_irr.py` (defaults: 2000 permutations, 1000 bootstraps, seed 42). Needs `requirements.txt` and the spaCy model (`python3 -m spacy download en_core_web_sm`). Embeddings: Qwen3-Embedding-0.6B with the instruction `Instruct: Embed aroma/flavor descriptors.` Each descriptor is cleaned first: spelling standardisation, spaCy lemmatisation, stop-word removal (negation and degree words kept at this step, tasting-note filler such as "aroma" and "taste" dropped), standardisation of synonym variants (burned/burnt, chocolaty/chocolate, and so on), and removal of words that are not aroma or flavor descriptors (comparison, intensity, evaluation and mouthfeel words such as more, less, strong, thinner, better, bad, watery; a descriptor left with no words is missing). The raw to cleaned map is in `irr/outputs/cleaned_descriptors.csv`. Outputs go to `irr/outputs/`. The docstring of the script defines the method.

## Result (default settings, semantic kappa [95% participant-bootstrap CI])

| Field | Stimulation | Sham |
|---|---|---|
| notesaroma | 0.068 [0.037, 0.104] | 0.068 [0.041, 0.097] |
| flavor_notes | 0.057 [0.033, 0.086] | 0.063 [0.033, 0.096] |

Agreement is above chance but very low: participants' descriptors are barely closer to each other for the same sample than for different samples. Thresholded versions are in `irr/outputs/semantic_irr_report.md`. The scale of kappa depends on the embedding (bge-small and all-mpnet give about 0.02 to 0.04), so compare across conditions and fields within one model. "n\\a" (not available) answers are treated as missing, not as a descriptor (see Corrections).

## Stimulation vs sham (exploratory)

`python3 irr/compare_conditions.py` tests delta = kappa(stimulation) - kappa(sham) per field, same pipeline and model. All 34 participants contribute to both conditions, so the CI is a paired participant bootstrap (2000) and the p-value a permutation test that swaps each participant's stimulation and sham descriptor sets (2000). Holm over the two fields. Output: `irr/outputs/condition_comparison.csv`.

| Field | Stimulation | Sham | Delta [95% CI] | p (perm) | p (Holm) |
|---|---|---|---|---|---|
| notesaroma | 0.068 | 0.068 | +0.000 [-0.034, 0.038] | 0.99 | 1.0 |
| flavor_notes | 0.057 | 0.062 | -0.006 [-0.038, 0.027] | 0.72 | 1.0 |

No evidence of a difference in between-participant agreement; the intervals are about +/-0.03 around zero, against kappas of about 0.06 to 0.07.

### Does cleaning or the model drive it?

`python3 irr/cleaning_sensitivity.py` repeats the comparison under Qwen with the cleaning steps on or off (raw, each step alone, lemma + stop words, all steps without the descriptors-only filter, and the main pipeline), and under bge-small and all-mpnet with raw, no-filter and main cleaning. Table: `irr/outputs/cleaning_sensitivity.md`. In every run the stimulation vs sham difference is within about +/-0.01 and every interval includes zero; its sign changes between runs, so it is noise around zero. Cleaning changes kappa little within a model (Qwen `notesaroma`: 0.057 to 0.068); the descriptors-only filter raises it slightly (0.062 and 0.065 without it, 0.068 and 0.068 with it), so non-descriptor words added a little noise but did not create or hide a condition difference. The model changes the scale (bge and mpnet about 0.03 to 0.04).

## SCA flavor wheel mapping (alternative pipeline, exploratory)

`python3 irr/sca_mapping.py` maps each cleaned word to a node of the SCA flavor wheel (`data/SCA flavor wheel.csv`): wheel terms and category names match automatically (longest match first, e.g. "dark chocolate"); `data/sca_aliases.csv` (hand-written, 65 entries, written after viewing the data, please review) maps generic and near-synonym words to a node at any level (fruit -> family 2_fruity, nut -> 8b_nutty, sourness and acidic -> 3a_sour, apple -> 2c_other fruit) or drops colour and mouthfeel words; any other word goes to `5_other` (or is dropped in the second variant). A descriptor becomes the set of its nodes. Three measures: Qwen embedding of the node terms, node-set Jaccard overlap, and family-level (level 1) Jaccard overlap, each with the same chance correction and the paired stimulation vs sham comparison. Coverage is nearly complete: only 38 word occurrences have no wheel home (butter 10, cream 8, ripe 7, milk 2, and singletons), so 361 of 361 `notesaroma` and 366 of 366 `flavor_notes` descriptors keep at least one node (`5_other` kept); dropping them removes 7 and 2 descriptors. Full tables and the word-to-node audit: `irr/outputs/sca_mapping_report.md` and `sca_mapping_audit.csv`.

Kappa per condition, other kept (stimulation / sham):

| Measure | notesaroma | flavor_notes |
|---|---|---|
| embedding | 0.073 / 0.080 | 0.060 / 0.060 |
| node Jaccard | 0.016 / 0.018 | 0.011 / 0.011 |
| family Jaccard | 0.090 / 0.078 | 0.068 / 0.064 |

Stimulation minus sham, other kept: embedding -0.006 [-0.043, 0.034] (aroma) and +0.000 [-0.030, 0.032] (flavor); node Jaccard -0.001 and +0.000; family Jaccard +0.012 [-0.040, 0.070] and +0.005 [-0.033, 0.045]; all p >= 0.67, and the dropped variant gives the same picture. Mapping to the wheel leaves the conclusion unchanged: agreement is low at every level (exact-node agreement is near chance, family-level agreement is the highest) and does not differ between stimulation and sham. The wheel mapping is not the main pipeline.

## Corrections

- A first version embedded the 67 "n\a" non-responses (41 in `notesaroma`, 26 in `flavor_notes`) as if they were a descriptor, so they counted as perfect agreement between participants. They are now missing. All kappas and comparisons above come from the corrected run; earlier numbers (kappa about 0.05, differences +0.002 and -0.005) were from the uncorrected version.
- The descriptors-only filter and its word list (`NON_DESCRIPTORS`) were written after viewing the vocabulary, so the pipeline is exploratory. It became the main pipeline after a sensitivity run showed it changed kappa slightly and the condition comparison not at all.

## Caveats

- The flavour notes are the second text column, whose header in the file is `bitter, roasted`; it is called `flavor_notes` here.
- Chance shuffles each participant's descriptors across the 6 items, so it keeps their vocabulary and removes item-specific agreement. Items are not split into coffee and repeat.
- The spelling fixes, synonym variants and filler stop words were listed after viewing the data, so the cleaning is exploratory.
- `data/tDCS.csv` is participant data and is committed locally; decide before adding a remote.
