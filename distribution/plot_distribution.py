#!/usr/bin/env python3
"""Radar plot of the family endorsement analysis (descriptive): the 9 SCA wheel families are the axes; each condition is a polygon whose radius is the
mean endorsement rate (share of tastings, per participant, averaged over participants) of that family. Left panel aroma notes, right panel flavor notes;
red = stimulation, blue = sham. Rates are those of distribution/outputs/family_endorsement.csv (manual mapping, paired participants only: n = 32 aroma,
33 flavor). The caption reports the tests. Output: distribution/outputs/distribution_plot.pdf and .png"""
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent / "outputs"
fe = pd.read_csv(OUT / "family_endorsement.csv")
om = pd.read_csv(OUT / "family_endorsement_omnibus.csv").set_index("field")
omc = pd.read_csv(OUT / "family_endorsement_omnibus_cosine.csv").set_index("field")
fams = list(fe[fe.field == "notesaroma"].family)  # wheel order (families 1 to 9)
label = [("chemical / papery /\\nmusty" if f.startswith("other") else f).replace("\\n", "\n") for f in fams]
ang = np.linspace(0, 2 * np.pi, len(fams), endpoint=False)
CC = {"stimulation": "#c0392b", "sham": "#2471a3"}
RMAX = 0.5

fig, axes = plt.subplots(1, 2, figsize=(11.5, 6.0), subplot_kw=dict(polar=True))
for ax, (field, title) in zip(axes, [("notesaroma", "Aroma notes"), ("flavor_notes", "Flavor notes")]):
    d = fe[fe.field == field].set_index("family").loc[fams]
    for cond, col in (("stimulation", "rate_stimulation"), ("sham", "rate_sham")):
        v = d[col].to_numpy()
        a, r = np.append(ang, ang[0]), np.append(v, v[0])
        ax.plot(a, r, color=CC[cond], lw=2, marker="o", ms=4.5, label=cond)
        ax.fill(a, r, color=CC[cond], alpha=0.14)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(ang)
    ax.set_xticklabels(label, fontsize=8.5)
    ax.set_ylim(0, RMAX)
    ax.set_yticks([0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_yticklabels(["0.1", "0.2", "0.3", "0.4", "0.5"], fontsize=7, color="0.4")
    ax.set_rlabel_position(22)
    ax.grid(color="0.8", lw=0.7)
    ax.tick_params(axis="x", pad=8)
    ax.set_title(f"{title} (n = {int(d.n.iloc[0])} participants)", fontsize=10.5, pad=22)
axes[0].legend(loc="lower left", bbox_to_anchor=(-0.12, -0.08), fontsize=9, frameon=False)
caption = (
    "Endorsement rate of the 9 SCA wheel families (share of tastings in which a participant's descriptor contains a word that maps to the family, averaged over "
    "participants), stimulation (red) vs sham (blue). Descriptive.\\n"
    f"Tests (paired sign-flip permutation, exploratory): aroma omnibus over the 9 families p = {om.loc['notesaroma', 'p_perm']:.3f}, q = {om.loc['notesaroma', 'q_bh']:.3f} "
    f"(cosine-mapping sensitivity q = {omc.loc['notesaroma', 'q_bh']:.3f}); flavor omnibus p = {om.loc['flavor_notes', 'p_perm']:.2f}, q = {om.loc['flavor_notes', 'q_bh']:.2f}; "
    f"no single family reaches q < {fe.q_bh.min():.2f} (BH over 18 family tests), so the differences between the polygons for individual families are not significant."
).replace("\\n", "\n")
fig.tight_layout(rect=(0, 0.1, 1, 1))
fig.text(0.03, 0.015, "\n".join("\n".join(textwrap.wrap(par, 165)) for par in caption.split("\n")), fontsize=7.6, ha="left", va="bottom", color="0.2")
fig.savefig(OUT / "distribution_plot.pdf", bbox_inches="tight")
fig.savefig(OUT / "distribution_plot.png", dpi=200, bbox_inches="tight")
