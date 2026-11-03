# the-zuza-vector

Free-text coffee descriptors of the tDCS study (`data/tDCS.csv`): do stimulation and sham differ in how much participants agree (`irr/`) and in which flavor families they endorse (`distribution/`)? Exploratory and descriptive; all cleaning and mapping rules were written after viewing the data.

- `irr/`: between-participant semantic agreement (IRR) within each condition, and stimulation vs sham.
- `distribution/`: wheel-family endorsement, stimulation vs sham (README in that folder).
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

## Corrections

- An early version embedded the 67 "n\\a" non-responses (41 in `notesaroma`, 26 in `flavor_notes`) as if they were a descriptor, which counted as perfect agreement between participants. They are now missing; all numbers come from the corrected run.
- Earlier variants (other embedding models, cleaning-step ablations, thresholded agreement, a wheel-anchored space) were removed from the repository to keep one main analysis and one sensitivity; they are in the git history (last state before removal: `ef6795a`). In those, the stimulation vs sham difference was within about +/-0.01 of zero in every run.

## Caveats

- The cleaning rules (spelling fixes, synonym variants, filler and non-descriptor words) were written after viewing the data, so the analysis is exploratory.
- Chance shuffles each participant's descriptors across the 6 items of a condition, which keeps their vocabulary and removes item-specific agreement; items are not split into coffee and repeat.
- The second text column has the header `bitter, roasted` in the file; it is called `flavor_notes` here.
