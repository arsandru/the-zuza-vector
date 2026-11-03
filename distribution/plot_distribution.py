#!/usr/bin/env python3
"""Plot of the family endorsement analysis (distribution/outputs/family_endorsement*.csv): per wheel family, the difference in endorsement
rate (stimulation - sham) with its 95% participant-bootstrap CI, for aroma and flavor; manual mapping (main) as filled markers, cosine mapping
(sensitivity) as open markers. Omnibus p and q (BH) of the main analysis in the panel titles. Output: distribution/outputs/distribution_plot.pdf and .png"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent / "outputs"
man, cos = pd.read_csv(OUT / "family_endorsement.csv"), pd.read_csv(OUT / "family_endorsement_cosine.csv")
om, omc = pd.read_csv(OUT / "family_endorsement_omnibus.csv"), pd.read_csv(OUT / "family_endorsement_omnibus_cosine.csv")
fams = list(man[man.field == "notesaroma"].family)
label = {f: ("chemical / papery / musty" if f.startswith("other") else f) for f in fams}

fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharey=True)
for ax, (field, title) in zip(axes, [("notesaroma", "Aroma notes"), ("flavor_notes", "Flavor notes")]):
    for i, f in enumerate(fams):
        for d, off, filled in ((man, -0.12, True), (cos, 0.12, False)):
            r = d[(d.field == field) & (d.family == f)].iloc[0]
            ax.errorbar(r["diff"], i + off, xerr=[[r["diff"] - r.ci_low], [r.ci_high - r["diff"]]], fmt="o", color="#2c3e50", mfc="#2c3e50" if filled else "white",
                        ms=5.5, capsize=2.5, lw=1.2)
    o, oc = om[om.field == field].iloc[0], omc[omc.field == field].iloc[0]
    ax.axvline(0, color="0.5", lw=0.8, ls="--")
    ax.set_title(f"{title}\nomnibus, manual: p = {o.p_perm:.3f}, q = {o.q_bh:.3f}\nomnibus, cosine: p = {oc.p_perm:.3f}, q = {oc.q_bh:.3f}", fontsize=9)
    ax.set_xlabel("endorsement rate: stimulation - sham")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axes[0].set_yticks(range(len(fams)))
axes[0].set_yticklabels([label[f] for f in fams], fontsize=9)
axes[0].invert_yaxis()
axes[0].plot([], [], "o", color="#2c3e50", label="manual mapping (main)")
axes[0].plot([], [], "o", color="#2c3e50", mfc="white", label="cosine mapping (sensitivity)")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, fontsize=8, frameon=False, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.045))
fig.text(0.5, 0.005, "points: mean paired difference with 95% participant-bootstrap CI (n = 32 aroma, 33 flavor); no single family reaches q < 0.25; exploratory",
         ha="center", fontsize=7, color="0.4")
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(OUT / "distribution_plot.pdf", bbox_inches="tight")
fig.savefig(OUT / "distribution_plot.png", dpi=200, bbox_inches="tight")
