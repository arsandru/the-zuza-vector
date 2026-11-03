#!/usr/bin/env python3
"""Plot of the numeric ICC vs semantic agreement check (irr/outputs/numeric_check_icc.csv): agreement per condition and stimulation - sham difference,
with the draft's reported overall ICC(A,1) for reference. Output: irr/outputs/numeric_check_plot.pdf and .png"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

OUT = Path(__file__).resolve().parent / "outputs"
D = pd.read_csv(OUT / "numeric_check_icc.csv")
rows = [  # label, kind, measure, version prefix
    ("overall rating, ICC(A,1)", "numeric", "overall", "ICC(A,1)"),
    ("fragrance, ICC(A,1)", "numeric", "fragrance", "ICC(A,1)"),
    ("flavour, ICC(A,1)", "numeric", "flavour", "ICC(A,1)"),
    ("aroma notes, semantic kappa", "semantic", "notesaroma", "consistency"),
    ("flavor notes, semantic kappa", "semantic", "flavor_notes", "consistency"),
]
DRAFT = {"sham": (0.134, 0.027, 0.261), "stimulation": (0.091, 0.009, 0.209), "diff": -0.043}
COL = {"stimulation": "#c0392b", "sham": "#2471a3"}


def get(kind, meas, ver, cond):
    return D[(D.kind == kind) & (D.measure == meas) & (D.version.str.startswith(ver)) & (D.condition == cond)].iloc[0]


fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True, gridspec_kw=dict(width_ratios=[1.2, 1]))
ypos = {}
y = 0
ylabels = []
ypos["draft"] = y
ylabels.append("overall rating, ICC(A,1), as reported in the draft")
y += 1
for lab, *_ in rows:
    ypos[lab] = y
    ylabels.append(lab + (" (replication)" if lab.startswith("overall") else ""))
    y += 1
for cond, off in (("stimulation", -0.13), ("sham", 0.13)):
    v, lo, hi = DRAFT[cond]
    a.errorbar(v, ypos["draft"] + off, xerr=[[v - lo], [hi - v]], fmt="s", color=COL[cond], mfc="white", ms=6, capsize=2.5, lw=1.2)
    for lab, kind, meas, ver in rows:
        r = get(kind, meas, ver, cond)
        a.errorbar(r.value, ypos[lab] + off, xerr=[[r.value - r.ci_low], [r.ci_high - r.value]], fmt="o", color=COL[cond], ms=6, capsize=2.5, lw=1.2)
b.errorbar(DRAFT["diff"], ypos["draft"], fmt="s", color="0.25", mfc="white", ms=6)
for lab, kind, meas, ver in rows:
    r = get(kind, meas, ver, "stimulation - sham")
    b.errorbar(r.value, ypos[lab], xerr=[[r.value - r.ci_low], [r.ci_high - r.value]], fmt="o", color="0.25", ms=6, capsize=2.5, lw=1.2)
a.axvline(0, color="0.6", lw=0.8, ls="--")
b.axvline(0, color="0.6", lw=0.8, ls="--")
a.set_yticks(range(len(ylabels)))
a.set_yticklabels(ylabels, fontsize=8.5)
a.invert_yaxis()
a.set_xlabel("ICC or semantic kappa (95% CI)")
b.set_xlabel("stimulation - sham (95% CI)")
a.set_title("Agreement per condition", fontsize=10)
b.set_title("Condition difference", fontsize=10)
a.plot([], [], "o", color=COL["stimulation"], label="stimulation")
a.plot([], [], "o", color=COL["sham"], label="sham")
a.plot([], [], "s", color="0.3", mfc="white", label="draft (reported)")
a.legend(fontsize=8, frameon=False, loc="lower right")
for ax in (a, b):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.text(0.5, 0.005, "intervals: participant bootstrap for the replication, fragrance, flavour and semantic rows; as reported for the draft (no interval for its difference); exploratory",
         ha="center", fontsize=7, color="0.4")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "numeric_check_plot.pdf", bbox_inches="tight")
fig.savefig(OUT / "numeric_check_plot.png", dpi=200, bbox_inches="tight")
