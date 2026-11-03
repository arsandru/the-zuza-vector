#!/usr/bin/env python3
"""Plot of the IRR results (irr/outputs/irr_summary.csv and irr_comparison.csv): kappa per condition and stimulation - sham difference,
main (centered) space as filled markers, sensitivity (plain) space as open markers. Output: irr/outputs/irr_plot.pdf and .png"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent / "outputs"
S = pd.read_csv(OUT / "irr_summary.csv")
C = pd.read_csv(OUT / "irr_comparison.csv")
FIELDS = ["notesaroma", "flavor_notes"]
COL = {"stimulation": "#c0392b", "sham": "#2471a3"}
SP = {"centered (main)": (0.0, True), "plain (sensitivity)": (0.16, False)}

fig, (a, b) = plt.subplots(1, 2, figsize=(9.2, 4.0), gridspec_kw=dict(width_ratios=[1.15, 1]))
for k, f in enumerate(FIELDS):
    for j, cond in enumerate(["stimulation", "sham"]):
        for sp, (off, filled) in SP.items():
            r = S[(S.field == f) & (S.condition == cond) & (S.space == sp)].iloc[0]
            x = k + (j - 0.5) * 0.42 + off - 0.08
            a.errorbar(x, r.semantic_kappa, yerr=[[r.semantic_kappa - r.ci_low], [r.ci_high - r.semantic_kappa]], fmt="o", color=COL[cond],
                       mfc=COL[cond] if filled else "white", ms=7, capsize=3, lw=1.4)
a.axhline(0, color="0.5", lw=0.8, ls="--")
a.set_xticks(range(2))
a.set_xticklabels(["aroma notes", "flavor notes"])
a.set_ylabel("semantic kappa (chance = 0)")
a.set_title("Agreement between participants", fontsize=10)
for cond in COL:
    a.plot([], [], "o", color=COL[cond], label=cond)
a.plot([], [], "o", color="0.3", label="centered space (main)")
a.plot([], [], "o", color="0.3", mfc="white", label="plain space (sensitivity)")
a.set_ylim(-0.005, 0.112)
h, l = a.get_legend_handles_labels()
for k, f in enumerate(FIELDS):
    for sp, (off, filled) in SP.items():
        r = C[(C.field == f) & (C.space == sp)].iloc[0]
        x = k + off - 0.08
        b.errorbar(x, r.delta, yerr=[[r.delta - r.ci_low], [r.ci_high - r.delta]], fmt="o", color="0.15", mfc="0.15" if filled else "white", ms=7, capsize=3, lw=1.4)
for k, f in enumerate(FIELDS):
    qm = C[(C.field == f) & (C.space == "centered (main)")].iloc[0].q_bh
    qp = C[(C.field == f) & (C.space == "plain (sensitivity)")].iloc[0].q_bh
    b.text(k + 0.04 - 0.08, 0.062, f"q = {qm:.2f} / {qp:.2f}", fontsize=8, ha="center", va="center")
b.axhline(0, color="0.5", lw=0.8, ls="--")
b.set_xticks(range(2))
b.set_xticklabels(["aroma notes", "flavor notes"])
b.set_ylabel("kappa(stimulation) - kappa(sham)")
b.set_title("Stimulation vs sham", fontsize=10)
b.set_xlim(-0.5, 1.6)
b.set_ylim(-0.06, 0.07)
for ax in (a, b):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.legend(h, l, fontsize=8, frameon=False, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.045))
fig.text(0.5, 0.005, "points: kappa or difference with 95% participant-bootstrap CI; q (BH) main / sensitivity space; exploratory", ha="center", fontsize=7, color="0.4")
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.savefig(OUT / "irr_plot.pdf", bbox_inches="tight")
fig.savefig(OUT / "irr_plot.png", dpi=200, bbox_inches="tight")
