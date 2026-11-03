#!/usr/bin/env python3
"""Stimulation vs sham: Jensen-Shannon distance between the distributions of SCA wheel nodes, at each wheel level (exploratory).

Descriptors are cleaned (irr/semantic_irr.py, main pipeline) and mapped to wheel nodes (wheel_mapping.py; unmapped words -> `5_other`).
Per text field (notesaroma, flavor_notes) and condition, each descriptor contributes one count to every node it contains, rolled up to the
level: level 1 = family (9), level 2 = category, level 3 = term (a category without terms on the wheel counts as its own term). A node
mapped coarser than the level (e.g. "fruit" -> family at levels 2 and 3, `5_other` at levels 2 and 3) is not resolved there and is left out
of that level's distributions; the counts kept are reported.
Statistic: Jensen-Shannon distance (square root of the base-2 JS divergence, 0 = identical, 1 = disjoint) between the pooled stimulation
and sham distributions. Sparse counts bias it upward, so the reference is a paired permutation test: every participant's stimulation and
sham descriptor sets are swapped with probability 1/2 (n = --n-perm); p = share of swaps with a distance at least as large (+1 correction),
and the excess over the mean swapped distance is reported. Holm over the 6 tests (3 levels x 2 fields).
Outputs (distribution/outputs/): jsd_by_level.csv, jsd_node_proportions.csv (every node: counts, proportions, contribution to the divergence)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import wheel_mapping as wm

sir = wm.sir
OUT_DIR = Path(__file__).resolve().parent / "outputs"
LEVELS = {1: "family", 2: "category", 3: "term"}


def level_label(node: str, k: int, children: set[str]) -> str | None:
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
    args = ap.parse_args()

    nodes, auto, _ = wm.build_vocab()
    amap = wm.load_aliases(nodes)
    children = {n.rsplit("|", 1)[0] for n in nodes if "|" in n}
    df = sir.load(sir.DEFAULT_INPUT)
    parts = sorted(df["subject"].unique())
    rng = np.random.default_rng(args.seed)
    rows, prop_rows = [], []

    for col, fname in sir.FIELDS.items():
        sets = []
        for x in df[col]:
            cl = None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)
            sets.append(None if cl is None else (wm.map_words(cl, auto, amap, True)[0] or None))
        df["nset"] = sets
        for k, lname in LEVELS.items():
            counts = {}  # (participant, condition) -> {label: n}
            for r in df.itertuples():
                if r.nset is None:
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
            rows.append(dict(field=fname, level=k, level_name=lname, n_nodes=len(vocab), count_stimulation=int(A.sum()), count_sham=int(B.sum()),
                             js_distance=obs, swap_null_mean=null.mean(), swap_null_p95=np.percentile(null, 95), excess=obs - null.mean(),
                             p_perm=(1 + (null >= obs - 1e-12).sum()) / (1 + args.n_perm)))
            contrib = contributions(A.sum(0), B.sum(0))
            for lab in vocab:
                i = ix[lab]
                term = nodes[lab][1] if lab in nodes else lab
                prop_rows.append(dict(field=fname, level=k, node=lab, term=term, count_stimulation=int(A[:, i].sum()), count_sham=int(B[:, i].sum()),
                                      prop_stimulation=A[:, i].sum() / A.sum(), prop_sham=B[:, i].sum() / B.sum(), js_contribution=contrib[i]))
            print(f"{fname:12} level {k} {lname:8} nodes {len(vocab):3} counts {int(A.sum())}/{int(B.sum())}  JS {obs:.3f}  "
                  f"null {null.mean():.3f} (p95 {np.percentile(null, 95):.3f})  p = {rows[-1]['p_perm']:.3f}")

    res = pd.DataFrame(rows)
    order = res["p_perm"].argsort().to_numpy()
    adj, run = np.empty(len(res)), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(res) - rank) * res["p_perm"].iloc[i]))
        adj[i] = run
    res["p_holm"] = adj
    OUT_DIR.mkdir(exist_ok=True)
    res.to_csv(OUT_DIR / "jsd_by_level.csv", index=False, float_format="%.6f")
    pd.DataFrame(prop_rows).to_csv(OUT_DIR / "jsd_node_proportions.csv", index=False, float_format="%.6f")
    pd.set_option("display.width", 200)
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
