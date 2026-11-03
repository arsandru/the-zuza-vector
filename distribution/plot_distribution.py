#!/usr/bin/env python3
"""Descriptive map of the participants' words in flavor-wheel space (distribution analysis).

Space: the wheel vocabulary (every wheel term and terminal category) embedded with Qwen3-Embedding-0.6B (aroma/flavor instruction), centered on
its mean, and reduced to 2 dimensions by a linear discriminant analysis fitted on the wheel vocabulary only (the two directions that best separate
the 9 wheel families; 15 principal components first, ridge-regularised). Participants' words are projected, never used to fit. Background: the wheel terms (grey, family names
at the family centroid). Foreground: the words and phrases participants used that the mapping places on the wheel (manual mapping; same cleaning
as the analyses), embedded and projected into the same plane; area = number of occurrences in that condition, colour = condition (red stimulation, blue sham; both
conditions on the same panel). Left panel aroma notes, right panel flavor notes. Purely descriptive; the caption reports the tests (distribution/family_endorsement.py).
Output: distribution/outputs/distribution_plot.pdf and .png
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import wheel_mapping as wm

sir = wm.sir
OUT = Path(__file__).resolve().parent / "outputs"

nodes, auto, _ = wm.build_vocab()
amap = wm.load_aliases(nodes)
df = sir.load(sir.DEFAULT_INPUT)
embed = wm.make_embedder(sir.DEFAULT_MODEL, sir.INSTRUCTION)

# wheel vocabulary: level-3 terms plus categories without terms
has_child = {n.rsplit("|", 1)[0] for n in nodes if "|" in n}
vocab = [n for n in nodes if n.count("|") == 2 or (n.count("|") == 1 and n not in has_child)]
vtext = [nodes[n][1] for n in vocab]
vfam = [n.split("|")[0] for n in vocab]
Ev = embed(vtext)
mean = Ev.mean(axis=0)
# LDA on the wheel vocabulary: first reduce to K principal components (SVD), then take the two directions that best separate the 9 families
# (between-family over within-family scatter, ridge-regularised). numpy/einsum only (spurious matmul warnings with sklearn and @ here).
K = 15
_, _, Vt = np.linalg.svd(Ev - mean, full_matrices=False)
Vk = Vt[:K]
Zv = np.einsum("nd,kd->nk", Ev - mean, Vk)
yv = np.array(vfam)
cls = sorted(set(yv))
mu_c = np.stack([Zv[yv == c].mean(axis=0) for c in cls])
Sw = sum(np.einsum("nk,nl->kl", Zv[yv == c] - mu_c[i], Zv[yv == c] - mu_c[i]) for i, c in enumerate(cls)) / (len(Zv) - len(cls))
Sb = sum((yv == c).sum() * np.outer(mu_c[i] - Zv.mean(axis=0), mu_c[i] - Zv.mean(axis=0)) for i, c in enumerate(cls)) / len(Zv)
Sw += 0.05 * np.trace(Sw) / K * np.eye(K)
evals, evecs = np.linalg.eig(np.linalg.solve(Sw, Sb))
W = np.real(evecs[:, np.argsort(-np.real(evals))[:2]])
evals = np.sort(np.real(evals))[::-1]
explained = evals[:2] / evals.sum()  # share of the between-family discriminability in each axis
comps = np.einsum("kj,kd->jd", W, Vk)
proj = lambda E: np.einsum("nd,jd->nj", E - mean, comps)
Pv = proj(Ev)

# participants' units per field and condition
fields = {}
for col, fname in sir.FIELDS.items():
    cnt = {c: {} for c in sir.CONDITIONS}
    tot = {c: 0 for c in sir.CONDITIONS}
    for row in df.itertuples():
        x = df.at[row.Index, col]
        if pd.isna(x) or not str(x).strip():
            continue
        cl = sir.clean_descriptor(x)
        if cl is None:
            continue
        ns, log = wm.map_words(cl, auto, amap, False)
        units = {u for u, node, src in log if node not in ("IGNORE", "dropped")}
        if not ns:
            continue
        tot[row.condition] += 1
        for u in units:
            cnt[row.condition][u] = cnt[row.condition].get(u, 0) + 1
    fields[fname] = (cnt, tot)
all_units = sorted({u for f in fields.values() for c in sir.CONDITIONS for u in f[0][c]})
Eu = embed(all_units)
Pu = dict(zip(all_units, proj(Eu)))
assert np.isfinite(Pv).all() and all(np.isfinite(v).all() for v in Pu.values())

pal = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666", "#1f78b4"]
fams = sorted(set(vfam))
fcol = dict(zip(fams, pal))
flabel = {f: ("chemical / papery / musty" if f == "5_other" else nodes[f][1]) for f in fams}

CC = {"stimulation": "#c0392b", "sham": "#2471a3"}
SZ = lambda n: 14 + 9 * n
fig, axes = plt.subplots(1, 2, figsize=(12.5, 6.4), sharex=True, sharey=True)
for ax, (field, title) in zip(axes, [("notesaroma", "Aroma notes"), ("flavor_notes", "Flavor notes")]):
    cnt, tot = fields[field]
    ax.scatter(Pv[:, 0], Pv[:, 1], s=14, color="0.75", linewidths=0, zorder=1)
    for f in fams:
        m = np.array([v == f for v in vfam])
        ax.text(Pv[m, 0].mean(), Pv[m, 1].mean(), flabel[f], color="0.35", fontsize=8, fontweight="bold", ha="center", va="center", zorder=2,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.6))
    pts = []
    for u in all_units:
        ns = {c: cnt[c].get(u, 0) for c in sir.CONDITIONS}
        if sum(ns.values()) == 0:
            continue
        dx = 0.00042 * np.sqrt(SZ(max(ns.values())))  # the two conditions' points of a word are offset left/right so both stay visible
        for c, sign in (("stimulation", -1), ("sham", 1)):
            if ns[c] > 0:
                pts.append((ns[c], c, (Pu[u][0] + sign * dx, Pu[u][1])))
    for n, c, xy in sorted(pts, key=lambda t: -t[0]):  # larger points first so smaller ones stay visible on top
        ax.scatter(xy[0], xy[1], s=SZ(n), color=CC[c], edgecolor="0.2", linewidths=0.4, alpha=0.75, zorder=3)
    for u in all_units:
        if cnt["stimulation"].get(u, 0) + cnt["sham"].get(u, 0) >= 22:
            ax.text(Pu[u][0], Pu[u][1] + 0.03, u, fontsize=7, ha="center", va="bottom", zorder=5)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(f"LD1 ({100 * explained[0]:.0f}% of discriminability)")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axes[0].set_ylabel(f"LD2 ({100 * explained[1]:.0f}%)")
handles = [plt.scatter([], [], s=60, color=CC[c], alpha=0.7, label=c) for c in sir.CONDITIONS]
handles += [plt.scatter([], [], s=SZ(n), color="0.6", label=f"{n} occurrences") for n in (2, 10, 30)]
handles += [plt.scatter([], [], s=14, color="0.75", label="wheel term")]
fig.legend(handles=handles, loc="lower center", ncol=6, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.115))
fig.tight_layout(rect=(0, 0.19, 1, 1))
om = pd.read_csv(OUT / "family_endorsement_omnibus.csv").set_index("field")
omc = pd.read_csv(OUT / "family_endorsement_omnibus_cosine.csv").set_index("field")
fe = pd.read_csv(OUT / "family_endorsement.csv")
caption = (
    "Flavor-wheel space: wheel terms (small grey points, family names in grey) and the words participants used that map to the wheel (coloured points; area = occurrences, red = stimulation, blue = sham, "
    "both conditions in the same panel, the two points of a word offset left and right), in the plane (LD1, LD2) that best separates the wheel families (discriminant analysis fitted on the wheel vocabulary only; Qwen3-Embedding-0.6B); green/vegetative, sweet and nutty/cocoa overlap in this plane. Descriptive map; "
    "the 2D projection distorts distances.\n"
    f"Tests (family endorsement, paired sign-flip permutation over 9 wheel families; exploratory): aroma omnibus p = {om.loc['notesaroma', 'p_perm']:.3f}, "
    f"q = {om.loc['notesaroma', 'q_bh']:.3f} (cosine-mapping sensitivity q = {omc.loc['notesaroma', 'q_bh']:.3f}); flavor omnibus p = {om.loc['flavor_notes', 'p_perm']:.2f}, "
    f"q = {om.loc['flavor_notes', 'q_bh']:.2f}; no single family reaches q < {fe.q_bh.min():.2f} (BH over 18 family tests). Differences in the map are not tests of individual words."
)
import textwrap

fig.text(0.02, 0.01, "\n".join("\n".join(textwrap.wrap(par, 190)) for par in caption.split("\n")), fontsize=7.4, ha="left", va="bottom", color="0.2")
fig.savefig(OUT / "distribution_plot.pdf", bbox_inches="tight")
fig.savefig(OUT / "distribution_plot.png", dpi=200, bbox_inches="tight")
print(f"saved; {len(vocab)} wheel terms, {len(all_units)} participant units")
