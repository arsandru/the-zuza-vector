# Coffee descriptor analysis

Agreement between participants and flavor-family profiles in the free-text notes of the cathodal tDCS coffee-tasting study

34 participants, stimulation vs sham, within-subject. Exploratory analysis. Code and outputs: private repository arsandru/the-zuza-vector, 2026-11-03.

## Summary

- **Agreement.** Participants who taste the same coffee write descriptors that are only slightly closer to each other than their own habitual vocabulary would predict (semantic kappa about 0.055 to 0.07, both conditions). We found no evidence that stimulation changes this: the stimulation minus sham differences are within 0.01 of zero, with 95% intervals of about plus or minus 0.04.
- **Flavor families.** Flavor notes show no difference between conditions in which of the nine wheel families are endorsed (omnibus q = 0.54). Aroma notes show a difference in the overall profile (p = 0.018, q = 0.035), with more sweet and sour/fermented and less floral and green/vegetative descriptors under stimulation. No single family reaches q below 0.25, and the omnibus keeps the same pattern but falls to a trend with an automatic word-to-wheel mapping (q = 0.057) and when words without a wheel home are kept as a category (q = 0.062).
- **Link to the numeric ICC in the draft.** Numeric and semantic agreement are both low and show the same broad pattern (no clear stimulation effect). Two cautions: we could not reproduce the draft's numeric ICC from the data file (we obtain 0.069 and 0.052 for sham and stimulation, the draft reports 0.134 and 0.091), and the similarity of two participants' descriptors is not related to the closeness of their scores (Spearman rho between -0.03 and +0.01).
- **Status.** All analyses are exploratory; the cleaning rules and the word-to-wheel mapping were written after looking at the data. Section 6 lists four points where we need input.

## 1. Data and design

Thirty-four participants without professional coffee training each tasted two coffees (Brazil, Kenya) three times as the cups cooled, once under cathodal tDCS and once under sham. After every tasting they gave numeric attribute ratings and two free-text notes: aroma notes and flavor notes. Per condition this gives 6 tastings per participant (2 coffees x 3 repeated ratings), and every participant contributes to both conditions, so all comparisons are paired. The participant is the unit of analysis throughout. Descriptors that were missing ("n\\a") or that contained no aroma or flavor word after cleaning are treated as missing, not as an answer.

## 2. Methods in brief

### Cleaning the free text

Spelling standardisation (33 rules), lemmatisation (spaCy), stop-word removal (negation and degree words kept at this step), merging of synonym variants (burned and burnt, chocolaty and chocolate), and removal of words that are not aroma or flavor descriptors (comparison, intensity, evaluation, mouthfeel words such as more, thinner, better, watery). The word lists were written after viewing the vocabulary of about 270 distinct words.

### Agreement between participants

Each cleaned descriptor is embedded with Qwen3-Embedding-0.6B using the instruction "Embed aroma/flavor descriptors". In the main space the embeddings are centered on the mean descriptor vector; the plain space is a sensitivity analysis. Observed agreement is the mean cosine similarity between two participants' descriptors for the same tasting, over all participant pairs. Chance agreement is obtained by shuffling each participant's descriptors across the 6 tastings of a condition, which preserves their vocabulary and removes the link to the tasting. Semantic kappa is (observed - chance) / (1 - chance). Intervals are participant bootstraps. Stimulation minus sham uses a paired participant bootstrap and a permutation test that swaps each participant's two conditions; q is the Benjamini-Hochberg FDR over the two fields.

### Flavor-family profiles

Words are mapped to the nine families of the SCA flavor wheel (floral, fruity, sour/fermented, green/vegetative, chemical/papery/musty, roasted, spices, nutty/cocoa, sweet) through the wheel's own terms and a hand-written alias table (for example nut to nutty, sourness to sour); words with no wheel home are left out. At each tasting a participant endorses a family if any word maps to it. Per participant we compute the endorsement rate per condition and family and the paired difference stimulation minus sham. The omnibus test is the sum over the nine families of the squared paired t, judged against a sign-flip permutation (each participant's conditions swapped at random, 10000 times); per family we report a participant bootstrap interval, the permutation p and q (BH over the 18 family tests). A second analysis uses an automatic word-to-wheel rule (cosine similarity to category prototypes) in place of the alias table.

## 3. Agreement between participants

| Space | Field | Kappa, stimulation | Kappa, sham | Stimulation - sham | p | q |
| --- | --- | --- | --- | --- | --- | --- |
| Centered space (main) | Aroma notes | 0.070 \[0.038, 0.105\] | 0.069 \[0.041, 0.100\] | +0.001 \[-0.034, +0.041\] | 0.95 | 0.95 |
| Centered space (main) | Flavor notes | 0.055 \[0.032, 0.084\] | 0.065 \[0.033, 0.100\] | -0.009 \[-0.042, +0.024\] | 0.58 | 0.95 |
| Plain space (sensitivity) | Aroma notes | 0.068 \[0.037, 0.104\] | 0.068 \[0.041, 0.097\] | +0.000 \[-0.033, +0.039\] | 0.99 | 0.99 |
| Plain space (sensitivity) | Flavor notes | 0.057 \[0.033, 0.086\] | 0.063 \[0.033, 0.096\] | -0.006 \[-0.038, +0.027\] | 0.72 | 0.99 |

Semantic kappa per condition and stimulation minus sham difference for aroma and flavor notes

Left: semantic kappa per condition with 95% participant-bootstrap intervals (filled: centered space, main; open: plain space, sensitivity). Right: stimulation minus sham difference with q (main / sensitivity). Exploratory.

Agreement is above chance in every case (intervals exclude zero) and very low. There is no evidence of a condition difference for aroma or flavor, and the two embedding spaces give the same answer. Kappa values depend on the embedding and cleaning, so they should be compared between conditions within an analysis, not with kappas from other studies.

## 4. Comparison with the numeric ICC

The draft reports ICC(A,1) of the overall rating (two-way random effects, absolute agreement, single ratings; targets are coffee x repeated rating, raters are participants): sham 0.134 \[0.027, 0.261\], stimulation 0.091 \[0.009, 0.209\], difference -0.043. The design matches the semantic analysis (same raters, same six targets per condition, analysed per condition). One difference is conceptual: absolute agreement counts a rater's own scale offset as disagreement, whereas the semantic chance model removes each participant's habitual vocabulary. An absolute-agreement version of the semantic statistic gives practically identical values (aroma 0.066 and 0.067, flavor 0.062 and 0.053, sham and stimulation), so this does not matter in these data.

| Measure | Sham | Stimulation | Stimulation - sham |
| --- | --- | --- | --- |
| Numeric, overall rating, ICC(A,1) | 0.069 | 0.052 | -0.018 \[-0.177, +0.105\] |
| Numeric, fragrance, ICC(A,1) | 0.021 | 0.025 | +0.004 \[-0.111, +0.159\] |
| Numeric, flavour, ICC(A,1) | 0.079 | 0.034 | -0.045 \[-0.182, +0.057\] |
| Semantic, aroma notes, kappa | 0.069 | 0.070 | +0.001 \[-0.035, +0.039\] |
| Semantic, flavor notes, kappa | 0.064 | 0.056 | -0.009 \[-0.045, +0.027\] |

**The numeric ICC in the draft does not reproduce from the data file.** With the overall rating in the shared data, REML with crossed random effects for target and rater gives ICC(A,1) of 0.069 for sham and 0.052 for stimulation (difference -0.018); a classical ANOVA ICC on complete raters agrees. The draft's point estimates are about twice as large, the intervals overlap, and the ordering is the same. Defining the targets as coffee only or repeated rating only does not reproduce them either. Possible reasons are a different data version, a different target or exclusion definition, or the implementation in the intraclass package. We need the draft's analysis code or data subset to resolve this.

Both kinds of agreement are low and neither shows a condition effect for aroma. For flavor, both point to slightly lower agreement under stimulation, with intervals that include zero (the semantic intervals are about four times narrower). However, the two measures are not tied together at the level of pairs of participants rating the same tasting:

| Descriptor field | Score | Pairs | Spearman rho |
| --- | --- | --- | --- |
| Aroma notes | fragrance | 5260 | -0.010 \[-0.072, +0.053\] |
| Flavor notes | flavour | 5414 | -0.020 \[-0.082, +0.038\] |
| Aroma notes | overall | 5171 | +0.012 \[-0.048, +0.064\] |
| Flavor notes | overall | 5323 | -0.034 \[-0.110, +0.046\] |

Participants who score a coffee alike do not detectably describe it alike. Numeric agreement is itself very low (fragrance ICC about 0.02), which limits what a correlation can show, but the data do not support treating the two as one construct. The semantic result should be described as agreement in descriptors, not agreement in ratings.

## 5. Flavor-family profiles

| Field | Participants | Omnibus T | p | q, alias mapping | q, cosine mapping |
| --- | --- | --- | --- | --- | --- |
| Aroma notes | 32 | 21.7 | 0.018 | 0.035 | 0.057 |
| Flavor notes | 33 | 8.4 | 0.542 | 0.542 | 0.418 |

Radar plot of endorsement rates of the nine wheel families under stimulation and sham, for aroma and flavor notes

Endorsement rate of the nine SCA wheel families (share of tastings in which a participant's descriptor contains a word that maps to the family, averaged over participants). Red: stimulation, blue: sham. Descriptive. Tests (paired sign-flip permutation, exploratory): aroma omnibus p = 0.018, q = 0.035 (q = 0.057 with the cosine mapping); flavor omnibus p = 0.54, q = 0.54; no single family reaches q below 0.25, so differences between the polygons for individual families are not significant.

### Aroma notes, per family

| Family | Stimulation | Sham | Difference | p | q |
| --- | --- | --- | --- | --- | --- |
| floral | 0.07 | 0.13 | -0.06 \[-0.12, -0.01\] | 0.042 | 0.25 |
| fruity | 0.33 | 0.32 | +0.01 \[-0.07, +0.11\] | 0.765 | 1.00 |
| sour/fermented | 0.16 | 0.11 | +0.06 \[+0.00, +0.12\] | 0.081 | 0.29 |
| green/vegetative | 0.07 | 0.14 | -0.07 \[-0.13, -0.02\] | 0.020 | 0.25 |
| chemical / papery / musty | 0.03 | 0.03 | +0.00 \[-0.04, +0.05\] | 1.000 | 1.00 |
| roasted | 0.26 | 0.29 | -0.03 \[-0.12, +0.06\] | 0.500 | 0.90 |
| spices | 0.07 | 0.11 | -0.03 \[-0.07, +0.01\] | 0.187 | 0.48 |
| nutty/cocoa | 0.38 | 0.39 | -0.01 \[-0.10, +0.08\] | 0.865 | 1.00 |
| sweet | 0.23 | 0.14 | +0.08 \[+0.01, +0.15\] | 0.041 | 0.25 |

### Flavor notes, per family

| Family | Stimulation | Sham | Difference | p | q |
| --- | --- | --- | --- | --- | --- |
| floral | 0.11 | 0.07 | +0.04 \[-0.02, +0.09\] | 0.225 | 0.51 |
| fruity | 0.49 | 0.46 | +0.02 \[-0.08, +0.12\] | 0.688 | 1.00 |
| sour/fermented | 0.26 | 0.27 | -0.01 \[-0.09, +0.07\] | 0.792 | 1.00 |
| green/vegetative | 0.10 | 0.08 | +0.02 \[-0.02, +0.06\] | 0.395 | 0.79 |
| chemical / papery / musty | 0.08 | 0.08 | +0.00 \[-0.05, +0.06\] | 1.000 | 1.00 |
| roasted | 0.29 | 0.21 | +0.08 \[-0.00, +0.16\] | 0.074 | 0.29 |
| spices | 0.09 | 0.08 | +0.01 \[-0.05, +0.07\] | 0.747 | 1.00 |
| nutty/cocoa | 0.35 | 0.30 | +0.05 \[-0.02, +0.13\] | 0.187 | 0.48 |
| sweet | 0.12 | 0.12 | +0.00 \[-0.06, +0.07\] | 0.929 | 1.00 |

Rates are endorsements per usable tasting, differences are stimulation minus sham with participant-bootstrap intervals, and q is BH over the 18 family tests.

The aroma profile differs overall, with the pattern spread over several families and wide intervals; no single family can be singled out. The condition effect does not differ between the three tastings (aroma p = 0.99, flavor p = 0.18). With 32 to 33 participants, only differences of about 0.15 or more in a family's endorsement rate can be detected reliably. A secondary descriptive analysis (Jensen-Shannon distance between the pooled distributions, at family, category and term level, and by tasting) shows nothing that survives FDR (family level: aroma notes p = 0.051, q = 0.16; flavor notes p = 0.699, q = 0.70).

## 6. Limitations and points where we need input

### Limitations

- The analyses are exploratory. Spelling fixes, synonym merges, non-descriptor words and the alias table were chosen after viewing the data.
- The aroma profile result falls to a trend (q = 0.057 and 0.062) with the cosine mapping or when words without a wheel home are kept as a category.
- The chance baseline shuffles descriptors across the 6 tastings of a condition; coffee and repeated tasting are not separated.
- Participants are novices with condensed training; free-text notes have a small vocabulary and the embedding only approximates flavor similarity.
- Power is limited (32 to 34 participants, at most six tastings per condition). Absence of a detected difference is not evidence of equal agreement or equal profiles.

### Input needed

- **Numeric ICC.** Could we get the analysis code or exact data subset behind the draft's ICC(A,1) values so that the discrepancy can be resolved before the semantic agreement is reported next to them?
- **Alias table.** The word-to-wheel table (77 rows) was drafted by us and determines the family results. A review by someone with sensory expertise would be valuable.
- **Wording.** Agreement should be reported as agreement in descriptors, and the aroma family result as suggestive; is this acceptable for the manuscript, and should the family analysis go into the paper or the supplement?
- **Data fields.** The data file has a `group` column (A to D) that we did not use. What does it encode, and should it enter the analysis? If descriptors of the seven-person reference panel exist, they could also be used to check the wheel mapping.

## 7. Reproducibility

All results are produced by scripts in the repository (`irr/semantic_irr.py`, `irr/numeric_check.py`, `distribution/family_endorsement.py` and companions), with fixed seeds (42). `EXPLAINER.md` in the repository describes every step in detail and `README.md` holds the full result tables.