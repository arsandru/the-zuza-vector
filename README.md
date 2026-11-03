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

`python3 irr/compare_conditions.py` tests delta = kappa(stimulation) - kappa(sham) per field, same pipeline and model. All 34 participants contribute to both conditions, so the CI is a paired participant bootstrap (2000) and the p-value a permutation test that swaps each participant's stimulation and sham descriptor sets (2000). BH-FDR over the two fields. Output: `irr/outputs/condition_comparison.csv`.

| Field | Stimulation | Sham | Delta [95% CI] | p (perm) | q (BH) |
|---|---|---|---|---|---|
| notesaroma | 0.068 | 0.068 | +0.000 [-0.034, 0.038] | 0.99 | 0.99 |
| flavor_notes | 0.057 | 0.062 | -0.006 [-0.038, 0.027] | 0.72 | 0.99 |

No evidence of a difference in between-participant agreement; the intervals are about +/-0.03 around zero, against kappas of about 0.06 to 0.07.

### Does cleaning or the model drive it?

`python3 irr/cleaning_sensitivity.py` repeats the comparison under Qwen with the cleaning steps on or off (raw, each step alone, lemma + stop words, all steps without the descriptors-only filter, and the main pipeline), and under bge-small and all-mpnet with raw, no-filter and main cleaning. Table: `irr/outputs/cleaning_sensitivity.md`. In every run the stimulation vs sham difference is within about +/-0.01 and every interval includes zero; its sign changes between runs, so it is noise around zero. Cleaning changes kappa little within a model (Qwen `notesaroma`: 0.057 to 0.068); the descriptors-only filter raises it slightly (0.062 and 0.065 without it, 0.068 and 0.068 with it), so non-descriptor words added a little noise but did not create or hide a condition difference. The model changes the scale (bge and mpnet about 0.03 to 0.04).

## SCA flavor wheel mapping

The wheel mapping (`distribution/wheel_mapping.py`, `data/SCA flavor wheel.csv`, `data/sca_aliases.csv`) is not used for the agreement analysis here (a trial of that, with no condition difference, was removed; it is in the git history at `afaa689`). It is used by the distribution analysis in `distribution/` (Jensen-Shannon distance between stimulation and sham at each wheel level).

## Agreement in a flavor-wheel space (alternative embedding space, exploratory)

`python3 irr/wheel_space_irr.py` embeds the same cleaned descriptors in a space defined by the SCA flavor wheel, with no descriptor aliases or mapping: the anchors are the 105 distinct terms, category names and family names of the wheel (`data/SCA flavor wheel.csv` only). A descriptor is embedded with Qwen (aroma/flavor instruction), described by its cosine similarity to every anchor, each anchor coordinate is z-scored across all descriptor occurrences (which also removes the generic component shared by all food words), and profiles are compared by cosine. Everything else (chance, kappa, bootstrap, paired comparison, BH-FDR) is as above. Anchors, standardisation and similarity were fixed in advance.

Space check on the wheel vocabulary (does similarity separate wheel terms of the same family or category from other pairs? AUC over 2485 term pairs; the two terms of a pair are removed from the anchors):

| Space | AUC same family | AUC same category |
|---|---:|---:|
| Qwen (plain) | 0.712 | 0.731 |
| Qwen centered on the descriptor mean | 0.774 | 0.817 |
| wheel space | 0.732 | 0.762 |

Kappa per condition (stimulation / sham): `notesaroma` 0.109 [0.060, 0.167] / 0.103 [0.054, 0.160]; `flavor_notes` 0.091 [0.047, 0.143] / 0.102 [0.055, 0.156]. Stimulation minus sham: +0.006 [-0.052, +0.073] (q = 0.86) and -0.010 [-0.063, +0.045] (q = 0.86). Kappa is about 1.5 times that of the plain Qwen space (0.057 to 0.068) and still low, and the comparison is unchanged: no evidence of a difference. Full tables: `irr/outputs/wheel_space_report.md`.

Reading: the wheel space does separate the wheel's families better than the plain space, but simply centering the plain space on the descriptor mean separates them better still, so the wheel anchoring itself adds little beyond removing the generic component. The higher kappa mostly reflects the removed baseline, not new agreement.

## Corrections

- A first version embedded the 67 "n\a" non-responses (41 in `notesaroma`, 26 in `flavor_notes`) as if they were a descriptor, so they counted as perfect agreement between participants. They are now missing. All kappas and comparisons above come from the corrected run; earlier numbers (kappa about 0.05, differences +0.002 and -0.005) were from the uncorrected version.
- The descriptors-only filter and its word list (`NON_DESCRIPTORS`) were written after viewing the vocabulary, so the pipeline is exploratory. It became the main pipeline after a sensitivity run showed it changed kappa slightly and the condition comparison not at all.

## Caveats

- The flavour notes are the second text column, whose header in the file is `bitter, roasted`; it is called `flavor_notes` here.
- Chance shuffles each participant's descriptors across the 6 items, so it keeps their vocabulary and removes item-specific agreement. Items are not split into coffee and repeat.
- The spelling fixes, synonym variants and filler stop words were listed after viewing the data, so the cleaning is exploratory.
- `data/tDCS.csv` is participant data and is committed locally; decide before adding a remote.
