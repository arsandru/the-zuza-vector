# Numeric and semantic IRR

Check of the semantic agreement analysis against the numeric ICC in the draft. Cathodal tDCS coffee-tasting study, 34 participants. Exploratory. Code: irr/numeric_check.py (repository the-zuza-vector).

Semantic and numeric IRR agree on the broad picture but are not demonstrably measuring the same agreement, and I could not reproduce the draft's numeric ICC.

## 1. I could not replicate the draft's ICC

- **Replication:** overall rating, ICC(A,1) with REML on the shared data file. Sham 0.069 \[0.012, 0.228\] and stimulation 0.052 \[0.012, 0.162\], difference −0.018. A classical ANOVA gives the same values.
- **Draft:** sham 0.134, stimulation 0.091, difference −0.043.
- **Comparison:** the draft's point estimates are about twice ours, the intervals overlap heavily, and the ordering is the same (sham above stimulation). Redefining the targets as coffee only or repeat only does not reproduce the draft either.
- **To resolve:** I need the draft's analysis code or data subset. It could be a different data version, different target or exclusion definitions, or the intraclass implementation. Until then, the draft's numeric numbers should not be assumed to match this data file.

## 2. The design is the same, with one difference that does not matter here

- **Same:** raters are participants, targets are coffee × repeated tasting (6 per condition), and each condition is analysed separately.
- **Difference:** ICC(A,1) counts a rater's own offset as disagreement. Our semantic kappa removes each participant's habitual vocabulary through its chance model, which is closer to ICC(C,1). An absolute-agreement analogue gives practically the same values: aroma 0.066 vs 0.069 and flavor 0.062 vs 0.064 (sham).

## 3. Level and pattern are similar

- **Level:** both are low. The semantic values are 0.055 to 0.07, and the numeric ones are 0.02 to 0.13.
- **Aroma:** neither shows a condition effect (fragrance +0.004, aroma notes +0.001).
- **Flavor:** both are slightly lower under stimulation (numeric flavour −0.045, semantic −0.009), and all intervals include zero.
- **Precision:** the semantic intervals are about four times narrower than the numeric ones.

## 4. The two measures are not linked at the pair level

- **Test:** for pairs of participants rating the same tasting, the absolute score difference was compared with descriptor similarity. Spearman rho runs from −0.03 to +0.01, and every interval includes zero.
- **Reading:** people who score a coffee alike do not detectably describe it alike. This test has limited power, because numeric agreement is itself very low (fragrance ICC about 0.02).
- **Wording:** the semantic result should be described as agreement in descriptors, not agreement in ratings.