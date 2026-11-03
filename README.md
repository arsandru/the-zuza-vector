# the-zuza-vector

Free-text coffee descriptors of the tDCS study (`data/tDCS.csv`): do stimulation and sham differ in how much participants agree (`irr/`) and in which flavor families they endorse (`distribution/`)? Exploratory and descriptive; all cleaning and mapping rules were written after viewing the data.

- `irr/`: between-participant semantic agreement (IRR) within each condition, and stimulation vs sham.
- `distribution/`: wheel-family endorsement, stimulation vs sham (summary below, details in the README of that folder).
- `data/`: `tDCS.csv`, `SCA flavor wheel.csv`, `sca_aliases.csv` (used by `distribution/` only). `tDCS.csv` is participant data; this repository is private.

## IRR (`irr/semantic_irr.py`)

Repurposed from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py` (three fixed raters over clusters) for 34 participants who each describe the same coffee samples. From the repository root: `python3 irr/semantic_irr.py` (2000 chance shuffles, 1000 bootstrap and swap iterations, seed 42; needs `requirements.txt` and `python3 -m spacy download en_core_web_sm`), then `python3 irr/plot_irr.py` for the figure. The docstring defines the method.

- **Cleaning** of each descriptor: spelling standardisation (33 misspelling and variant fixes), spaCy lemmatisation, stop-word removal (negation and degree words kept at this step, tasting-note filler dropped), standardisation of synonym variants (burned/burnt, chocolaty/chocolate), removal of words that are not aroma or flavor descriptors (comparison, intensity, evaluation and mouthfeel words such as more, less, strong, thinner, better, bad, watery; a descriptor left with no words is missing). "n\\a" answers are missing. The raw to cleaned map is `irr/outputs/cleaned_descriptors.csv`.
- **Embedding**: Qwen3-Embedding-0.6B with the instruction `Instruct: Embed aroma/flavor descriptors.` **Main space: embeddings centered on the occurrence-weighted mean descriptor embedding** (removes the component shared by all coffee descriptors), compared by cosine. **Sensitivity: the plain (uncentered) embeddings.**
- **Agreement**: rater = participant, item = coffee x repeated tasting (6 per condition), each condition and text field separately. Observed = mean cosine similarity of two participants' descriptors over all pairs that both answered an item. Chance = each participant's descriptors shuffled across the items of the condition. Semantic kappa = (observed - expected) / (1 - expected). 95% CI: participant bootstrap.
- **Stimulation vs sham**: all 34 participants contribute to both conditions, so the CI is a paired participant bootstrap and p comes from swapping each participant's stimulation and sham descriptor sets; BH-FDR q over the 2 fields within each space.

| Space | Field | Kappa stimulation [95% CI] | Kappa sham [95% CI] | Difference [95% CI] | p | q |
|---|---|---|---|---|---:|---:|
| centered (main) | notesaroma | 0.070 [0.038, 0.105] | 0.069 [0.041, 0.100] | +0.001 [-0.034, +0.041] | 0.95 | 0.95 |
| centered (main) | flavor_notes | 0.055 [0.032, 0.084] | 0.065 [0.033, 0.100] | -0.009 [-0.042, +0.024] | 0.58 | 0.95 |
| plain (sensitivity) | notesaroma | 0.068 [0.037, 0.104] | 0.068 [0.041, 0.097] | +0.000 [-0.033, +0.039] | 0.99 | 0.99 |
| plain (sensitivity) | flavor_notes | 0.057 [0.033, 0.086] | 0.063 [0.033, 0.096] | -0.006 [-0.038, +0.027] | 0.72 | 0.99 |

Agreement is above chance but very low in both conditions, and there is no evidence of a difference between stimulation and sham (differences of -0.009 to +0.001, intervals about +/-0.03 around zero). The two spaces agree (centering leaves kappa where the plain space had it, because the chance correction already removes the baseline similarity). Figure: `irr/outputs/irr_plot.pdf` and `.png`. The kappa scale depends on the embedding, so compare conditions within a space, not kappa values across studies.

## Distribution: wheel-family endorsement (`distribution/`)

Do stimulation and sham endorse different flavor families? Descriptors (same cleaning as the IRR) are mapped to the 9 families of the SCA flavor wheel (`data/SCA flavor wheel.csv` plus the hand-written `data/sca_aliases.csv`; words with no wheel home are left out). At each tasting a participant endorses a family if any word of the descriptor maps to it (a tasting without a usable descriptor is missing). The unit is the participant: endorsement rate per condition, field and family (aroma n = 32, flavor n = 33 participants with usable tastings in both conditions), paired difference stimulation - sham. Omnibus test per field: sum over the 9 families of the squared paired t against a paired sign-flip permutation (each participant's two conditions swapped, 10000 times); per family: bootstrap 95% CI, sign-flip p, BH-FDR q over the 18 family tests; BH q over the 2 omnibus tests. `python3 distribution/family_endorsement.py`, then `python3 distribution/plot_distribution.py`. Method details, secondary analyses and caveats: `distribution/README.md`.

| Field | Omnibus T | p | q (BH, 2 fields) | q with cosine mapping |
|---|---:|---:|---:|---:|
| notesaroma | 21.7 | 0.018 | 0.035 | 0.057 |
| flavor_notes | 8.4 | 0.542 | 0.542 | 0.418 |

Families with the largest differences (endorsement rate; all families in `distribution/outputs/family_endorsement_report.md`):

| Field | Family | Stimulation | Sham | Difference [95% CI] | p | q (BH, 18 tests) |
|---|---|---:|---:|---|---:|---:|
| notesaroma | sweet | 0.23 | 0.14 | +0.08 [+0.01, +0.15] | 0.041 | 0.25 |
| notesaroma | floral | 0.07 | 0.13 | -0.06 [-0.12, -0.01] | 0.042 | 0.25 |
| notesaroma | green/vegetative | 0.07 | 0.14 | -0.07 [-0.13, -0.02] | 0.020 | 0.25 |
| notesaroma | sour/fermented | 0.16 | 0.11 | +0.06 [+0.00, +0.12] | 0.081 | 0.29 |
| flavor_notes | roasted | 0.29 | 0.21 | +0.08 [-0.00, +0.16] | 0.074 | 0.29 |

Aroma: the family profiles differ overall (stimulation higher on sweet and sour/fermented, lower on floral and green/vegetative), but no single family reaches q below 0.25, the intervals are wide, and the omnibus sits on either side of q = 0.05 depending on the wheel mapping (manual q = 0.035, cosine mapping q = 0.057) and on how words with no wheel home are handled (kept as a separate category instead: q = 0.062), so I would call it suggestive, not robust. Flavor: no difference. The condition effect does not differ between the three tastings (aroma p = 0.99, flavor p = 0.18). With 32 to 33 participants only differences of roughly 0.15 or more in a family's endorsement rate can be detected reliably. Descriptive Jensen-Shannon analyses of the pooled distributions (all wheel levels, by tasting) are in `distribution/README.md`; none survives FDR. Figure: `distribution/outputs/distribution_plot.pdf` and `.png` (radar of the family endorsement rates, stimulation vs sham; the caption reports the tests).

## Corrections

- An early version embedded the 67 "n\\a" non-responses (41 in `notesaroma`, 26 in `flavor_notes`) as if they were a descriptor, which counted as perfect agreement between participants. They are now missing; all numbers come from the corrected run.
- Earlier variants (other embedding models, cleaning-step ablations, thresholded agreement, a wheel-anchored space) were removed from the repository to keep one main analysis and one sensitivity; they are in the git history (last state before removal: `ef6795a`). In those, the stimulation vs sham difference was within about +/-0.01 of zero in every run.

## Caveats

- The cleaning rules (spelling fixes, synonym variants, filler and non-descriptor words) were written after viewing the data, so the analysis is exploratory.
- Chance shuffles each participant's descriptors across the 6 items of a condition, which keeps their vocabulary and removes item-specific agreement; items are not split into coffee and repeat.
- The second text column has the header `bitter, roasted` in the file; it is called `flavor_notes` here.
