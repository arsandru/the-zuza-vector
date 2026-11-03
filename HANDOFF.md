# Handoff: the-zuza-vector (2026-11-03)

Read this first, then `README.md` (results), `EXPLAINER.md` (step-by-step method guide written for the supervised student) and `CLAUDE.md` (rules). Update or replace this file at the end of each session.

## What this repo is

Free-text coffee descriptors from a tDCS study (`data/tDCS.csv`: 34 participants, stimulation vs sham, 2 coffees x 3 repeated tastings per condition, two text fields: `notesaroma` and `flavor_notes`, the latter is the file's column headed `bitter, roasted`). Two analyses, both exploratory:

1. `irr/`: between-participant semantic agreement (IRR), within each condition, then stimulation vs sham. Repurposed from `altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py`.
2. `distribution/`: do stimulation and sham endorse different SCA flavor-wheel families.

Remote: https://github.com/arsandru/the-zuza-vector (private, branch `main`, local matches origin at `63a14ab` plus this handoff). The remote holds participant data (`data/tDCS.csv`); do not make the repo public without removing it.

## State of the analyses (all numbers are in `README.md` and the outputs)

**IRR (`irr/semantic_irr.py`, `irr/plot_irr.py`).** Per descriptor: spelling standardisation, spaCy lemmatisation, stop words, synonym standardisation, removal of non-descriptor words (more, less, strong, thinner, better, bad, watery ...), `n\a` and emptied descriptors are missing. Embedding: Qwen3-Embedding-0.6B with `Instruct: Embed aroma/flavor descriptors.` **Main space = embeddings centered on the occurrence-weighted mean descriptor embedding; sensitivity = plain embeddings.** Semantic kappa against a chance baseline (each participant's descriptors shuffled across the 6 items of a condition), participant bootstrap CIs, paired stimulation vs sham test (condition swap within participant), BH-FDR over the 2 fields. Result: kappa about 0.07 (aroma) and 0.055 to 0.065 (flavor), above chance but low; stimulation minus sham within +/-0.01, q 0.95 to 0.99.

**Distribution (`distribution/family_endorsement.py`, main).** Descriptors mapped to the 9 wheel families (wheel terms + `data/sca_aliases.csv`; words with no wheel home are left out). Participant-level endorsement rate per condition, field and family; omnibus sum of squared paired t with a paired sign-flip permutation; per family bootstrap CI, p, BH q over 18 tests; tasting interaction test. Aroma omnibus p = 0.018, q = 0.035 (cosine-mapping sensitivity q = 0.057; with no-home words kept as a separate category q = 0.062), flavor q = 0.54; no single family below q = 0.25. Reading agreed so far: suggestive for aroma, not robust, no single-family claims. Secondary descriptive analyses: Jensen-Shannon distance between pooled distributions (`jsd_by_level.py`, all levels, by tasting, cosine mapping) and `validate_cosine_mapping.py`; nothing survives FDR. Figure: radar plot (`plot_distribution.py`) with a caption that states the tests.

## Decisions made by the user (do not revisit without asking)

- IRR main space is the centered one, plain is the sensitivity; all other IRR variants (other embedding models, cleaning ablations, thresholded agreement, wheel-anchored space) were removed (last present in git at `ef6795a`).
- The descriptors-only filter (non-descriptor words removed) is part of the main cleaning pipeline.
- `n\a` is missing, not a descriptor (an early version embedded it and inflated agreement; fixed and documented in the README).
- FDR (Benjamini-Hochberg), not Holm, everywhere.
- The wheel mapping is not used for the IRR (no descriptor aliases there); it is used only in `distribution/`. Words with no wheel home are left out (they are IGNORE in the alias file). The wheel's own family 5 is `5_other` (chemical, papery/musty) and is kept apart from them.
- Manual mapping is main; cosine mapping (prototype = family name, category name and terms; family = parent of the predicted category) is a sensitivity run only.
- The distribution figure is a descriptive radar plot; significance goes in the caption only.

## Known issues and caveats

- **`data/sca_aliases.csv` is my draft** (77 rows: 61 map generic words and near-synonyms to a wheel node, 16 are IGNORE: colour and mouthfeel words and the ten no-home words). It has not been reviewed by the user; `distribution/outputs/cosine_mapping_validation.md` lists where the cosine rule disagrees. It determines the distribution results, so it should be checked.
- The aroma omnibus keeps its pattern but falls to a trend with the cosine mapping (q = 0.057) or when no-home words are kept as a category (q = 0.062); keep it labelled exploratory.
- Cleaning rules (spelling fixes, synonym variants, filler and non-descriptor word lists) were written after viewing the data.
- Chance baseline shuffles across the 6 items of a condition; items are not split into coffee and repeat. Power: single-family differences below about 0.15 are not detectable with 32 to 33 participants.
- Stale code that is harmless: `clean_descriptor` in `irr/semantic_irr.py` still has ablation switches (all on in the analyses); `distribution/wheel_mapping.py` still defines `OTHER = "unmapped"` and `jsd_by_level.py` a guard for it (no longer produced); `label_matrix` and `pair_stats` keep an unused threshold argument.
- Numpy on this machine raises spurious overflow warnings with `@` on large arrays (also inside sklearn PCA and `transform`): the scripts use `np.einsum` and numpy SVD instead; keep doing that.
- Participant ids and free-text descriptors are in the repo (private). Do not paste long verbatim passages into new files.

## How to run (from the repository root; system Python 3.9, no venv)

```
python3 irr/semantic_irr.py            # about 2 min; writes irr/outputs/irr_*.csv, irr_report.md, cleaned_descriptors.csv
python3 irr/plot_irr.py
python3 distribution/family_endorsement.py            # main; add --mapping cosine for the sensitivity run
python3 distribution/jsd_by_level.py                  # secondary; --mapping cosine, --levels 1 --stratify repeated_ratings
python3 distribution/validate_cosine_mapping.py
python3 distribution/plot_distribution.py             # radar plot (reads the output CSVs, no model)
```

Needs `requirements.txt` plus `python3 -m spacy download en_core_web_sm`; Qwen3-Embedding-0.6B is cached locally and runs on MPS. All seeds are 42. Re-running overwrites the tracked outputs; check `git status` and `git diff --stat` afterwards.

## Open items (none requested yet)

- Robustness checks added (`irr/robustness_checks.py`): seed stability (Monte Carlo error of the reported p-values about +/-0.02, nothing else moves) and kappa per tasting (aroma agreement higher for Brasil, flavor for Kenya; descriptive). Not yet committed.

- Numeric ICC of the draft (overall rating, ICC(A,1): sham 0.134, stimulation 0.091) does not replicate here (we get 0.069 and 0.052; see README section "Check against the numeric ICC of the draft" and `irr/numeric_check.py`). Needs the draft's analysis code or data subset to resolve. Semantic and numeric agreement are both low and show the same broad pattern but are not linked at the pair level (rho about 0).

- Review `data/sca_aliases.csv` with the user.
- Decide whether `distribution/`'s Jensen-Shannon analyses stay in the repo (they are secondary and descriptive) or are removed like the IRR variants.
- Optionally split IRR items into coffee and repeated tasting, and add an environment lockfile.

## Working practice

In this repository I committed and pushed after each change without being asked every time (the user asked to create the GitHub repo and later asked for each analysis step); confirm with the user whether they want commits and pushes only on request. Push needs `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin main` because the osxkeychain credential helper is invalid on this machine (`gh` is logged in as arsandru).
