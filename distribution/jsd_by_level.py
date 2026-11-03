#!/usr/bin/env python3
"""Stimulation vs sham: Jensen-Shannon distance between the distributions of SCA wheel nodes, at each wheel level (exploratory).

Descriptors are cleaned (irr/semantic_irr.py, main pipeline) and mapped to wheel nodes (wheel_mapping.py; words with no wheel home are left out).
Per text field (notesaroma, flavor_notes) and condition, each descriptor contributes one count to every node it contains, rolled up to the
level: level 1 = family (the 9 wheel families), level 2 = category, level 3 = term (a category without terms on the wheel counts as its own term). A node
mapped coarser than the level (e.g. "fruit" -> family at levels 2 and 3, `unmapped` at levels 2 and 3) is not resolved there and is left out
of that level's distributions; the counts kept are reported.
Statistic: Jensen-Shannon distance (square root of the base-2 JS divergence, 0 = identical, 1 = disjoint) between the pooled stimulation
and sham distributions. Sparse counts bias it upward, so the reference is a paired permutation test: every participant's stimulation and
sham descriptor sets are swapped with probability 1/2 (n = --n-perm); p = share of swaps with a distance at least as large (+1 correction),
and the excess over the mean swapped distance is reported. BH-FDR over all tests of the run (levels x fields x strata). --levels and --stratify restrict the levels and split the data by a column
(e.g. repeated_ratings; the swap then acts within each stratum).
Outputs (distribution/outputs/): jsd_by_level.csv, jsd_node_proportions.csv (every node: counts, proportions, contribution to the divergence)
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

import wheel_mapping as wm

sir = wm.sir
OUT_DIR = Path(__file__).resolve().parent / "outputs"
LEVELS = {1: "family", 2: "category", 3: "term"}


def level_label(node: str, k: int, children: set[str]) -> str | None:
    if node == wm.OTHER:  # catch-all: a family-level category only
        return node if k == 1 else None
    parts = node.split("|")
    if len(parts) >= k:
        return "|".join(parts[:k])
    return node if node not in children else None  # terminal node counts at deeper levels; a coarser non-terminal node is unresolved


def js_distance(p: np.ndarray, q: np.ndarray) -> float:
    p, q = p / p.sum(), q / q.sum()
    m = 0.5 * (p + q)

    def kl(a):
        nz = a > 0
        return float((a[nz] * np.log2(a[nz] / m[nz])).sum())

    return float(np.sqrt(max(0.5 * kl(p) + 0.5 * kl(q), 0.0)))


def contributions(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    p, q = p / p.sum(), q / q.sum()
    m = 0.5 * (p + q)
    out = np.zeros_like(p)
    for a, i in ((p, 0), (q, 1)):
        nz = a > 0
        out[nz] += 0.5 * a[nz] * np.log2(a[nz] / m[nz])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--levels", default="1,2,3", help="wheel levels to analyse, e.g. 1 for families only")
    ap.add_argument("--stratify", default="", help="analyse separately within each value of this column, e.g. repeated_ratings (Holm over all tests)")
    ap.add_argument("--mapping", choices=("manual", "cosine"), default="manual",
                    help="cosine: words mapped by the alias file to a wheel node (not to `unmapped`) are re-assigned to the nearest wheel category by cosine "
                         "(prototype = family name, category name and terms; family = parent of the category; see validate_cosine_mapping.py); "
                         "exact wheel terms and the alias file's `unmapped` and IGNORE entries are unchanged, and alias words are resolved to a "
                         "category only, so they are unresolved at level 3")
    args = ap.parse_args()

    nodes, auto, _ = wm.build_vocab()
    amap = wm.load_aliases(nodes)
    children = {n.rsplit("|", 1)[0] for n in nodes if "|" in n}
    df = sir.load(sir.DEFAULT_INPUT)
    cosine_cat = {}
    if args.mapping == "cosine":
        alias_units = sorted({u for col in sir.FIELDS for x in df[col] if not pd.isna(x) and str(x).strip() and (cl := sir.clean_descriptor(x))
                              for u, node, src in wm.map_words(cl, auto, amap, False)[1] if src == "alias" and node not in ("IGNORE", wm.OTHER)})
        embed = wm.make_embedder(sir.DEFAULT_MODEL, sir.INSTRUCTION)
        cats, fams, ctext, _ = wm.member_texts(nodes, "l123")
        texts = sorted({t for ts in ctext.values() for t in ts} | set(alias_units))
        Em = dict(zip(texts, embed(texts)))
        cid, Pc = wm.prototypes(ctext, Em)
        for u in alias_units:
            cosine_cat[u] = cid[int(np.argmax(np.einsum("d,kd->k", Em[u], Pc)))]
    parts = sorted(df["subject"].unique())
    args.levels = [int(x) for x in args.levels.split(",")]
    strata = sorted(df[args.stratify].unique()) if args.stratify else [None]
    suffix = ("" if args.mapping == "manual" else "_cosine") + (f"_by_{args.stratify}" if args.stratify else "") + \
             ("" if args.levels == [1, 2, 3] else "_levels" + "".join(map(str, args.levels)))
    rng = np.random.default_rng(args.seed)
    rows, prop_rows = [], []

    for col, fname in sir.FIELDS.items():
        sets = []
        for x in df[col]:
            cl = None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)
            if cl is None:
                sets.append(None)
                continue
            ns, log = wm.map_words(cl, auto, amap, False)
            if args.mapping == "cosine":
                ns = {cosine_cat.get(u, node) if src == "alias" else node for u, node, src in log if node not in ("IGNORE", "dropped")}
            sets.append(ns or None)
        df["nset"] = sets
        for sv, (k, lname) in itertools.product(strata, [(k, v) for k, v in LEVELS.items() if k in args.levels]):
            counts = {}  # (participant, condition) -> {label: n}
            for r in df.itertuples():
                if r.nset is None or (args.stratify and getattr(r, args.stratify) != sv):
                    continue
                labs = {level_label(n, k, children) for n in r.nset} - {None}
                d = counts.setdefault((r.subject, r.condition), {})
                for lab in labs:
                    d[lab] = d.get(lab, 0) + 1
            vocab = sorted({lab for d in counts.values() for lab in d})
            ix = {lab: i for i, lab in enumerate(vocab)}
            C = {c: np.zeros((len(parts), len(vocab))) for c in sir.CONDITIONS}
            for (sub, cond), d in counts.items():
                for lab, n in d.items():
                    C[cond][parts.index(sub), ix[lab]] = n
            A, B = C["stimulation"], C["sham"]
            obs = js_distance(A.sum(0), B.sum(0))
            null = np.empty(args.n_perm)
            for b in range(args.n_perm):
                sw = (rng.random(len(parts)) < 0.5)[:, None]
                null[b] = js_distance(np.where(sw, B, A).sum(0), np.where(sw, A, B).sum(0))
            rows.append(dict(field=fname, stratum=sv if args.stratify else "all", level=k, level_name=lname, n_nodes=len(vocab), count_stimulation=int(A.sum()), count_sham=int(B.sum()),
                             js_distance=obs, swap_null_mean=null.mean(), swap_null_p95=np.percentile(null, 95), excess=obs - null.mean(),
                             p_perm=(1 + (null >= obs - 1e-12).sum()) / (1 + args.n_perm)))
            contrib = contributions(A.sum(0), B.sum(0))
            for lab in vocab:
                i = ix[lab]
                term = nodes[lab][1] if lab in nodes else lab
                prop_rows.append(dict(field=fname, stratum=sv if args.stratify else "all", level=k, node=lab, term=term, count_stimulation=int(A[:, i].sum()), count_sham=int(B[:, i].sum()),
                                      prop_stimulation=A[:, i].sum() / A.sum(), prop_sham=B[:, i].sum() / B.sum(), js_contribution=contrib[i]))
            print(f"{fname:12} {args.stratify}={sv} level {k} {lname:8} nodes {len(vocab):3} counts {int(A.sum())}/{int(B.sum())}  JS {obs:.3f}  "
                  f"null {null.mean():.3f} (p95 {np.percentile(null, 95):.3f})  p = {rows[-1]['p_perm']:.3f}")

    res = pd.DataFrame(rows)
    res["q_bh"] = sir.bh_fdr(res["p_perm"])
    OUT_DIR.mkdir(exist_ok=True)
    res.to_csv(OUT_DIR / f"jsd_by_level{suffix}.csv", index=False, float_format="%.6f")
    pd.DataFrame(prop_rows).to_csv(OUT_DIR / f"jsd_node_proportions{suffix}.csv", index=False, float_format="%.6f")
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
