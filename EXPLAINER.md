# Explainer: what the two analyses do, step by step

This document is for a student who will work in this repository. It explains, for each main analysis, the question, the logic, and every methodological step, with the reasons behind each choice and the places where the choices are weak. Read it with the code open: every step names the file and function where it happens. Results and exact numbers are in `README.md`; the working rules and the state of the project are in `CLAUDE.md` and `HANDOFF.md`.

Everything here is **exploratory**. Nothing was pre-registered, and several rules (word lists, spelling fixes, the wheel mapping) were written after looking at the data. That does not make the analyses useless, but it changes how results are worded: we describe patterns and report uncertainty, and we do not claim confirmed effects.

## Contents

1. The study and the data
2. Ideas used in both analyses
3. Shared step: cleaning the free text
4. Analysis 1: how much do participants agree with each other? (`irr/`)
5. Analysis 2: do the conditions endorse different flavor families? (`distribution/`)
6. What we can and cannot conclude
7. Common mistakes
8. Exercises
9. Where things are in the code
10. Reading

---

## 1. The study and the data

`data/tDCS.csv` has 408 rows: 34 participants x 12 rows. Each participant tasted two coffees (Brasil and Kenya) in two conditions, **stimulation** (real tDCS) and **sham** (placebo stimulation). Within each condition and coffee the participant tasted the coffee three times in a row (`repeated_ratings` = 1, 2, 3). The `temperature` column falls across the three tastings (mean values about 60, 42 and 33 in the file's units), so the coffee cools as the tasting proceeds. So per condition a participant produced 2 coffees x 3 tastings = **6 tastings**, and the same 6 tastings exist in the other condition: the design is **within-participant (paired)**.

After each tasting the participant wrote two short free-text notes:

- `notesaroma`: what the coffee smelled of ("aroma notes");
- the second text column, headed `bitter, roasted` in the file, which we call `flavor_notes` ("flavor notes").

Examples of what participants write: `dark chocolate, hazelnut`, `Burned / more acidic`, `n\a` (no answer), `cacao`, `better aroma but burnt`. There is also a `group` column (A to D) that we do not use; what it encodes is not documented in this repository, so ask the supervisor before deciding whether it matters.

Three terms to keep straight:

- **Participant**: the unit of analysis. The 408 rows are not 408 independent observations; they are 12 observations from each of 34 people.
- **Tasting (item)**: one coffee x one repeated tasting, within a condition.
- **Descriptor**: the text a participant wrote at one tasting for one field.

Some descriptors are missing (`n\a`, empty) or become empty after cleaning. Missing is not the same as "wrote nothing relevant", and the analyses treat it that way (Section 3).

## 2. Ideas used in both analyses

**Exploratory versus confirmatory.** A confirmatory analysis fixes hypotheses and methods before seeing the data. Ours did not, so every p-value is a descriptive tool and every analysis is labelled exploratory in the figures and reports. The practical rule: never pick a method because it gives the clearest result. Choices are made on validity (does this step measure what we mean?), and the alternatives are run as sensitivity analyses and reported whatever they show.

**The participant is the unit.** People who wrote more descriptors, or who have several tastings, would dominate if we pooled all descriptors as if independent. This error is called pseudoreplication. Both analyses therefore (a) compute something per participant or (b) resample or shuffle whole participants.

**Paired design.** Because every participant has both conditions, the natural comparison is each participant against themselves. This removes between-person differences (some people simply write more fruit words) from the comparison and gives more power.

**Permutation tests.** To ask "could this difference arise by chance?" we need the distribution of the statistic when there is no effect. A permutation test builds it by re-labelling the data in a way that would not matter if there were no effect and recomputing the statistic many times. In a paired design the labels "stimulation" and "sham" are exchangeable within a participant under no effect, so we swap them per participant at random (probability 1/2). The p-value is the share of re-labellings whose statistic is at least as extreme as the observed one, with a +1 in numerator and denominator so that p is never exactly 0.

**Bootstrap confidence intervals.** To show how uncertain an estimate is, we resample participants with replacement (a participant can appear twice, another not at all), recompute the estimate in each resample, and take the 2.5th and 97.5th percentiles. We resample participants, not descriptors, for the same reason as above.

**Multiple tests and FDR.** Doing many tests produces some small p-values by chance. We control the false discovery rate with the Benjamini-Hochberg procedure and report **q-values** (BH-adjusted p). A q of 0.05 means that, among results at least that convincing, about 5% are expected to be false discoveries. The family over which q is computed is always stated (for example "over the 2 fields" or "over the 18 family tests"). We use FDR and not Holm on purpose (supervisor's choice for these exploratory analyses).

**Effect sizes with intervals.** Always report the size of a difference with its interval, not only p. "No evidence of a difference" is the correct wording for a null, not "no effect".

---

## 3. Shared step: cleaning the free text

File: `irr/semantic_irr.py`, function `clean_descriptor`. Both analyses start from the cleaned descriptors, and `irr/outputs/cleaned_descriptors.csv` shows raw and cleaned text side by side. **Always read this file**; it is the quickest way to see what the pipeline does to real data.

The aim is to make different spellings and inflections of the same idea identical, and to remove words that do not describe aroma or flavor, so that downstream comparisons are about content. Steps, in order:

1. **Non-responses.** `n\a` becomes missing (`None`). An early version of the code embedded `n\a` as if it were a descriptor; participants who both wrote `n\a` then "agreed perfectly". This was a bug and is fixed; it is a good example of why raw data and cleaned data must be inspected.
2. **Spelling standardisation.** Lowercase, collapse whitespace, and fix misspellings and spelling variants word by word (`pomegrannate` to `pomegranate`, `carmelized` to `caramelized`, `flavour` to `flavor`; 33 rules in `TYPO_FIXES`). The list was made by reading every word in both columns.
3. **Lemmatisation** (spaCy `en_core_web_sm`). Reduce words to their dictionary form so that `berries` and `berry`, `roasted` and `roast` match. Lemmatisers make mistakes (it read `rose`, the flower, as the verb `rise`), so a small override list (`KEEP_TOKEN`) exists.
4. **Stop words.** Remove very common words (the, of, but) using the scikit-learn English list, with two changes: negation and degree words (not, no, less, more, very) are kept at this step because they change meaning, and 27 tasting-note filler words (aroma, flavor, taste, notes, coffee, hint, bit, little ...) are removed because they carry no aroma or flavor information.
5. **Synonym standardisation.** Merge different forms of the same descriptor (`burned`, `burn` to `burnt`; `chocolaty` to `chocolate`; `sweeter`, `sweetish` to `sweet`; 35 rules in `LEMMA_CANON`).
6. **Non-descriptor removal.** Remove words that are not aroma or flavor descriptors: comparisons (more, less, better, same, before), intensity and degree (strong, weak, mild, slightly), evaluation (bad, worst), and mouthfeel or body (thin, thinner, watery, soft, smooth; 49 words in `NON_DESCRIPTORS`). A descriptor with nothing left becomes missing.

Worked example: `slightly sweeter, thinner` becomes `sweet`; `better aroma but burnt` becomes `burnt`; `same as before` becomes missing.

Why these steps and not others? Steps 1 to 4 are standard text preprocessing. Steps 5 and 6 are researcher decisions made after looking at the vocabulary (about 270 distinct words), so they are the most exploratory part. We checked that they do not change the conclusion: in earlier runs the stimulation-vs-sham comparison stayed within about 0.01 of zero with or without each step (those runs were removed from the repo to keep it simple; they are in git history, last present at commit `ef6795a`).

---

## 4. Analysis 1: how much do participants agree with each other? (`irr/`)

### 4.1 The question

When different participants taste the same coffee, do they write similar descriptors? "Inter-rater reliability" (IRR) measures this kind of agreement. Do the participants agree more or less under stimulation than under sham?

### 4.2 Why a special method

Classic IRR statistics (Cohen's or Fleiss' kappa, Krippendorff's alpha) treat answers as categories that either match or do not. Free text has hundreds of distinct strings, and `lemon` and `lime` are close, `lemon` and `smoky` are not. Counting only exact matches would call almost everything disagreement. So we measure **semantic similarity**: how close the meanings of two descriptors are, and a chance-corrected agreement built on it. The statistic is adapted from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py`, where three fixed raters labelled clusters; here the raters are 34 participants.

### 4.3 Step 1: turn each descriptor into a vector (embedding)

A text embedding model maps a piece of text to a list of numbers (a vector) so that texts with similar meaning get similar vectors. We use Qwen3-Embedding-0.6B. The model takes an **instruction** (`Instruct: Embed aroma/flavor descriptors.`) that tells it what kind of similarity matters; the instruction text is placed before every descriptor. Two descriptors are compared by the **cosine similarity** of their vectors: 1 means same direction (same meaning), 0 unrelated, negative opposite.

Each unique cleaned descriptor (524 of them) is embedded once.

### 4.4 Step 2: remove the shared background (centering)

Embeddings of any two coffee descriptors are already quite similar to each other, because they all share "this is a coffee word" content. In the plain space the average similarity between random pairs is about 0.66. That baseline does no harm to the final kappa (the chance correction subtracts it), but it makes the raw similarities hard to read.

In the **main (centered) space** we subtract the mean embedding of all descriptors (weighted by how often each occurs) and renormalise, so the shared component is gone: random pairs now have similarity near 0 and agreement shows up as a positive similarity. The **plain (uncentered) space is the sensitivity analysis**. The two give almost the same kappa (this is expected, see 4.7), which is reassuring.

### 4.5 Step 3: define raters, items and observed agreement

- **Rater** = participant. **Item** = a tasting (coffee x repeated tasting): 6 items per condition.
- Each condition and each field is analysed separately.
- For each item, take every pair of participants who both wrote a (non-missing) descriptor for it, and compute the cosine similarity between the two descriptors. The **observed agreement** is the mean of these similarities over all pairs of all 6 items.

So the question is: when two different people taste the same sample at the same moment, how similar are their words?

### 4.6 Step 4: what agreement would we expect by chance?

Two people who both write `chocolate` for every coffee agree, but not because they perceive the same sample; they simply use that word. Agreement beyond habit is what we care about. To estimate **chance agreement** we use a permutation: for each participant, shuffle their descriptors across the 6 items of that condition (so their Brasil descriptor may now sit on a Kenya item), recompute the mean pair similarity, and average over 2000 shuffles. This keeps each participant's own vocabulary and word frequencies and breaks the link between a descriptor and the particular tasting it described. That is exactly the agreement we expect if participants only use their habitual words.

### 4.7 Step 5: semantic kappa

`kappa = (observed - expected) / (1 - expected)`

0 means agreement is what habit alone would give; 1 means identical descriptors. Real numbers (centered space, aroma notes, stimulation): observed 0.074, expected 0.005, kappa = 0.070. Because the chance term already contains the baseline similarity, centering changes observed and expected together and leaves kappa nearly unchanged, which is why centered and plain agree (plain: observed 0.678, expected 0.655, kappa 0.068).

Caution: the scale of kappa depends on the embedding model and the cleaning, so a kappa of 0.07 is not "7% agreement" and cannot be compared with kappas from other studies or other models. Compare conditions within a space.

### 4.8 Step 6: uncertainty for one kappa

Resample participants with replacement (1000 times) and recompute kappa each time. Two technical details matter: a participant who appears twice in a resample must not be paired with their own copy (that would be a perfect, meaningless pair), and the chance term is recomputed in every resample (with 100 shuffles) because it depends on who is in the sample. The 2.5th and 97.5th percentiles are the 95% interval.

### 4.9 Step 7: stimulation versus sham

Compute `delta = kappa(stimulation) - kappa(sham)` per field.

- **Interval**: a paired bootstrap, resampling the same participants in both conditions.
- **p-value**: a permutation test. In each of 1000 iterations, every participant's stimulation and sham data are swapped with probability 1/2, delta is recomputed, and p is the share of iterations with |delta| at least as large as observed.
- **Multiple testing**: BH-FDR over the 2 fields, within each space.

### 4.10 Reading the result

Agreement is above chance (intervals exclude 0) but very low: two participants tasting the same coffee write words only slightly closer to each other than the same two people would by chance. The difference between conditions is about 0 (within +/-0.01) with intervals of about +/-0.03, so we find no evidence of a difference. Because the interval is that wide, we also cannot exclude a modest difference. Figure: `irr/outputs/irr_plot.png`.

Reasons agreement could be low even if participants perceive the same thing: participants are not trained panelists, descriptor vocabularies differ widely, the embedding only roughly captures flavor similarity, and with only 6 items per condition the chance baseline is coarse.

### 4.11 Run it

`python3 irr/semantic_irr.py` (about two minutes), then `python3 irr/plot_irr.py`. Outputs in `irr/outputs/`: `irr_summary.csv` (kappa per condition), `irr_comparison.csv` (delta, interval, p, q), `irr_report.md`, `cleaned_descriptors.csv`.

---

## 5. Analysis 2: do the conditions endorse different flavor families? (`distribution/`)

### 5.1 The question

Setting agreement aside, do participants name different *kinds* of flavors under stimulation and sham? For example, more sweet and fewer floral descriptors. To answer in a structured way we use the **SCA coffee flavor wheel**, a standard vocabulary of coffee flavors organised in three levels: 9 families (floral, fruity, sour/fermented, green/vegetative, other = chemical/papery/musty, roasted, spices, nutty/cocoa, sweet), 28 categories (for example berry, citrus fruit), and 71 specific terms (raspberry, lemon, ...). The file is `data/SCA flavor wheel.csv`. We analyse at the family level, where the counts are large enough.

### 5.2 Step 1: map words to the wheel

File: `distribution/wheel_mapping.py`, function `map_words`. Each cleaned descriptor is a short list of words. Each word (or two- or three-word phrase, matched longest first, so `dark chocolate` is one unit) is assigned to a node of the wheel:

1. **Wheel terms match automatically.** `hazelnut` matches the wheel term hazelnut (nutty/cocoa), `lemon` matches citrus fruit. (A few wheel terms cannot match automatically because cleaning removes one of their words, for example `under ripe`; these are skipped.)
2. **Aliases.** Participants write many words that are not wheel terms (`nut`, `fruit`, `sourness`, `burnt`, `apple`). `data/sca_aliases.csv` is a hand-written table that maps each such word to a wheel node at any level (`fruit` maps to the fruity family, `burnt` to the burnt category under roasted, `apple` to other fruit), or to `IGNORE` for words we drop (colour words like `dark` when not part of `dark chocolate`, mouthfeel words like `dry`, and ten words with no home on the wheel such as `butter`, `cream`, `milk`).
3. **Anything else is left out** (it has no wheel home).

The mapping reads the same cleaned text as Section 3, e.g. `dark chocolate, hazelnut` becomes two units mapped to cocoa (`dark chocolate`) and nutty (`hazelnut`), both in the nutty/cocoa family; `Burned / more acidic` becomes `burnt` (roasted family) and `acidic` (sour family).

**Important caveat.** The alias file (77 rows: 61 map to a wheel node, 16 are IGNORE) was written by hand after looking at the data. It is a series of judgement calls (is `tomato` green/vegetative? is `toast` burnt?) and it directly determines the results. Treat it as part of the analysis to be reviewed, and look at `distribution/outputs/cosine_mapping_validation.md` to see where an automatic rule disagrees.

### 5.3 Step 2: families endorsed per tasting

This is a check-all-that-apply (CATA) logic: for each tasting and field, a participant either endorses a family (at least one of their words maps to it) or not. A descriptor like `chocolate hazelnut` endorses nutty/cocoa (once, even though two words). A descriptor with no mapped word is **missing** at that tasting, not "endorsed nothing": we do not know what the participant would have said.

### 5.4 Step 3: participant-level endorsement rates and paired differences

For each participant, condition, field and family: **rate = (number of tastings endorsing the family) / (number of tastings with a mapped descriptor)**. A rate of 0.25 means the family appeared in a quarter of that participant's usable tastings. Then for each participant the paired difference `d = rate(stimulation) - rate(sham)`. Participants without any usable tasting in one of the conditions are left out of that field (32 for aroma, 33 for flavor of 34).

Working at participant level answers the pseudoreplication problem: one number per participant, per family, per condition.

### 5.5 Step 4: the omnibus test (do the profiles differ at all?)

We first ask one question per field before looking at single families: is there any overall difference between the 9-family profiles? For each family, a paired t statistic `t = mean(d) / (sd(d) / sqrt(n))`. The **omnibus statistic is T = sum of the squared t over the 9 families**. T is large when many families differ a little or a few differ a lot.

The null distribution of T comes from a **sign-flip permutation**: under no condition effect, `d` for a participant is as likely to be `-d`, so we multiply each participant's whole difference vector by +1 or -1 at random (equivalent to swapping their two conditions), recompute T, and repeat 10000 times. The same flips are used for aroma and flavor so that participants are treated consistently. `p` is the share of flips with T at least as large as observed; `q` is BH over the 2 fields.

Why an omnibus first? With 9 families x 2 fields there are 18 family tests; the omnibus is a single, more powerful, less multiplicity-burdened test of "is there a difference in profile".

### 5.6 Step 5: which families? (follow-up)

For each family: the mean difference in rate with a participant bootstrap 95% interval (10000 resamples), the sign-flip p-value of its own t, and **q = BH over all 18 family tests** (2 fields x 9 families). Read the interval (size and uncertainty) first, then q. With about 32 participants, only differences of roughly 0.15 or more in a family's endorsement rate can be detected reliably, so most family-level tests are underpowered.

### 5.7 Step 6: does the effect depend on the tasting?

The coffee cools across tastings 1 to 3. Could the condition effect change as it cools? For each participant, field and family, we compute the paired difference at each of the 3 tastings (rate over the 2 coffees), summarise the variation of the effect across tastings with a repeated-measures ANOVA F per family, sum the F values, and obtain p by permuting the tasting labels within each participant (if the effect is the same at all tastings, which tasting a difference belongs to does not matter). Only participants with usable descriptors at all three tastings in both conditions can be used (30 and 27). This is a test of **interaction**, which is the correct way to ask whether the effect differs across tastings; running a separate test per tasting and comparing which are "significant" would not be.

### 5.8 Sensitivity analyses

1. **Cosine mapping.** To see how much the result depends on the hand-written aliases, `--mapping cosine` replaces the alias assignments by an automatic rule: each wheel category is represented by a prototype (the mean embedding of its family name, its own name and its terms), and each alias word is assigned to the category with the highest cosine similarity; its family is the parent of that category. Exact wheel terms stay as they are. We validated the rule against the manual mapping (`validate_cosine_mapping.py`): it agrees with the manual mapping for 71% of word types at category level and 82% at family level (86% and 93% weighted by how often the words occur), and the disagreements are mostly debatable (is `smoky` tobacco or burnt?).
2. **Handling of words with no wheel home.** We left them out. An earlier version kept them as a separate catch-all category, which changed the aroma omnibus (q = 0.062 instead of 0.035). The README reports both.

### 5.9 The secondary analysis (Jensen-Shannon distance)

`jsd_by_level.py` compares the pooled distribution of wheel nodes under stimulation with that under sham using the **Jensen-Shannon distance** (a symmetric measure of how different two probability distributions are, 0 identical, 1 completely disjoint), at the family, category and term level, with a paired permutation test and the excess over the null mean (sparse counts inflate the raw distance). It was our first approach and is kept as a descriptive summary. It was demoted because it pools descriptors (so verbose participants weigh more), says nothing about which families differ, and is blind to a change in how many families are endorsed. Nothing in it survives FDR.

### 5.10 Reading the result

- Flavor notes: no difference in the family profiles (omnibus q = 0.54).
- Aroma notes: the omnibus is significant at FDR 5% (q = 0.035) with stimulation higher on sweet and sour/fermented and lower on floral and green/vegetative, **but** no single family reaches q below 0.25, the intervals are wide, the omnibus moves to q = 0.057 with the cosine mapping, and to 0.062 when no-home words are kept as a category. So we describe it as suggestive and not robust, and we make no claims about individual families.
- The effect does not detectably vary across the three tastings.

Figure: `distribution/outputs/distribution_plot.png`, a radar plot with the 9 families as axes and one polygon per condition (radius = mean endorsement rate), aroma left and flavor right. The plot is descriptive: polygons that look different are not necessarily different, and the caption reports the tests.

### 5.11 Run it

`python3 distribution/family_endorsement.py` (main; add `--mapping cosine` for the sensitivity run), `python3 distribution/plot_distribution.py`, and for the secondary analyses `jsd_by_level.py` and `validate_cosine_mapping.py`. Outputs in `distribution/outputs/` (`family_endorsement_report.md` has all tables in readable form).

---

## 6. What we can and cannot conclude

Can say:

- Participants' descriptors for the same coffee agree only slightly more than their habitual vocabulary would predict, in both conditions.
- We found no evidence that stimulation changes this agreement.
- For flavor notes we found no evidence of a difference in the families endorsed.
- For aroma notes there is a suggestive overall difference in the family profile (stimulation more sweet and sour, less floral and green) that depends on analysis choices and cannot be pinned on any single family.

Cannot say:

- That stimulation changes aroma perception. The data are free-text descriptors, the analysis is exploratory, and the aroma result is fragile.
- That conditions do not differ ("no evidence" is not "evidence of no difference"; with 32 to 34 participants only fairly large effects can be detected).
- Anything about individual families or individual words.

## 7. Common mistakes

- **Treating descriptors as independent.** Always aggregate to participants or resample participants.
- **Changing methods after seeing results.** If you add a cleaning rule or a mapping alias because it makes a difference "look right", record it and rerun everything with it as a labelled sensitivity analysis; do not quietly overwrite.
- **Equating "missing" with "not endorsed"** (or with a descriptor). Both mistakes appeared in this project's history (`n\a` embedded as a word) and changed the numbers.
- **Comparing kappa across embeddings** or with literature values.
- **Reporting "significant in aroma, not in flavor" as a difference between aroma and flavor.** That is not a test of a difference between fields.
- **Over-reading a plot.** The radar polygons and any 2D projection are for orientation; look at the intervals in the tables.
- **Forgetting multiplicity.** Always say what the q or the correction covers.
- **Editing outputs by hand.** Outputs are tracked in git and regenerated by scripts; after a rerun check `git status` and `git diff --stat` and note what changed numerically.

## 8. Exercises

1. Read `irr/outputs/cleaned_descriptors.csv` and find five descriptors you would clean differently. Add the rule, rerun, and describe what changed.
2. Work through one example by hand: pick one item (for example Brasil, tasting 1, stimulation), list the descriptors of the participants, compute two pairwise cosine similarities with a few lines of Python, and check them against the code.
3. Run `python3 irr/semantic_irr.py --seed 1` and `--seed 2`. Which numbers change? Which conclusions?
4. Switch off one cleaning step (the `clean_descriptor` flags) and recompute kappa. Does it change the conclusion?
5. Open `data/sca_aliases.csv`. Choose ten rows you disagree with, change them in a copy, and rerun `family_endorsement.py`. How sensitive is the omnibus?
6. Simulate power: take the observed per-participant rates, add a true difference of 0.10 to one family in the stimulation condition, and see how often the pipeline detects it.
7. Write a one-paragraph results section for a paper using only what Section 6 allows.

## 9. Where things are in the code

| Step | File | Function or place |
|---|---|---|
| Load data, cleaning, spelling lists | `irr/semantic_irr.py` | `load`, `clean_descriptor`, `TYPO_FIXES`, `LEMMA_CANON`, `NON_DESCRIPTORS`, `STOP_WORDS` |
| Pair similarity, chance, kappa | `irr/semantic_irr.py` | `pair_stats`, `expected`, `kappa` |
| Bootstrap and paired comparison | `irr/semantic_irr.py` | `kappa_of`, `compare`, `main` |
| FDR | `irr/semantic_irr.py` | `bh_fdr` |
| IRR figure | `irr/plot_irr.py` | |
| Wheel vocabulary and mapping | `distribution/wheel_mapping.py` | `build_vocab`, `load_aliases`, `map_words` |
| Endorsement analysis | `distribution/family_endorsement.py` | `tstats`, `rm_F`, `main` |
| Cosine mapping and validation | `distribution/wheel_mapping.py`, `validate_cosine_mapping.py` | `member_texts`, `prototypes` |
| Secondary analysis | `distribution/jsd_by_level.py` | |
| Radar figure | `distribution/plot_distribution.py` | |

## 10. Reading

- Benjamini, Y. and Hochberg, Y. (1995). Controlling the false discovery rate. *Journal of the Royal Statistical Society B*, 57, 289-300.
- Efron, B. and Tibshirani, R. (1993). *An Introduction to the Bootstrap*. Chapman and Hall.
- Good, P. (2005). *Permutation, Parametric, and Bootstrap Tests of Hypotheses*. Springer.
- Krippendorff, K. (2004). *Content Analysis: An Introduction to Its Methodology*. Sage (agreement measures for categorical data).
- Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37, 145-151 (Jensen-Shannon).
- Specialty Coffee Association, *Coffee Taster's Flavor Wheel* (the wheel in `data/SCA flavor wheel.csv`).
