#!/usr/bin/env python3
"""Robustness checks of the semantic IRR (irr/semantic_irr.py): Monte Carlo stability across seeds, and agreement per tasting (item).

1. Seed stability: the chance level, the bootstrap intervals and the permutation p-values of semantic_irr.py use random shuffles and resamples (seed 42).
   Here the full main-analysis computation (kappa per condition, bootstrap CI, stimulation vs sham difference with bootstrap CI and swap-test p, BH q over
   the 2 fields) is repeated with other seeds (--seeds, default 1 2 3) and compared with the reported seed-42 results in irr/outputs/irr_summary.csv and
   irr_comparison.csv. Reported: the spread (min to max) of every quantity across seeds.
2. Agreement per tasting: for each of the 6 items (coffee x repeated tasting) of a condition, the semantic kappa of that item = (mean pair similarity of
   the item - chance) / (1 - chance), with the chance level of the whole condition (as in the original per-cluster analysis) and a participant-bootstrap CI
   (chance level held at its full-sample value). Descriptive: it shows whether agreement differs between coffees or across cooling.
Outputs (irr/outputs/): seed_stability.csv, item_agreement.csv, robustness_report.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

import semantic_irr as sir


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--permutations", type=int, default=2000)
    ap.add_argument("--n-iter", type=int, default=1000)
    ap.add_argument("--boot-perms", type=int, default=100)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    df = sir.load(sir.DEFAULT_INPUT)
    items = sorted(df["item"].unique())
    lab = {c: df[c].map(lambda x: None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)) for c in sir.FIELDS}
    uniq = sorted({v for c in sir.FIELDS for v in lab[c].dropna()})
    idx = {v: i for i, v in enumerate(uniq)}
    E = sir.unit_rows(np.asarray(SentenceTransformer(sir.DEFAULT_MODEL).encode([sir.INSTRUCTION + u for u in uniq], batch_size=16, show_progress_bar=False), dtype=float))
    occ = np.array([sum((lab[c] == u).sum() for c in sir.FIELDS) for u in uniq], dtype=float)
    Ec = sir.unit_rows(E - np.average(E, axis=0, weights=occ))
    spaces = {"centered (main)": np.clip(np.einsum("ud,vd->uv", Ec, Ec), -1, 1), "plain (sensitivity)": np.clip(np.einsum("ud,vd->uv", E, E), -1, 1)}
    mats = {}
    for col, fname in sir.FIELDS.items():
        for cond in sir.CONDITIONS:
            sub = df[df["condition"] == cond].copy()
            sub["lbl"] = lab[col][sub.index]
            mats[(fname, cond)] = sir.label_matrix(sub, idx, items)[0]

    # ---- 1. seed stability -------------------------------------------------------------------------------------------------------
    rows = []
    for seed in args.seeds:
        comp = []
        for space, M in spaces.items():
            for fname in sir.FIELDS.values():
                for cond in sir.CONDITIONS:
                    L = mats[(fname, cond)]
                    P = L.shape[0]
                    rng = np.random.default_rng(seed)
                    ids = np.arange(P)
                    obs = sir.pair_stats(L, M, ids)[0]
                    exp = sir.expected(L, M, ids, args.permutations, rng)
                    bk = np.array([sir.kappa_of(L[bi], M, bi, args.boot_perms, rng) for bi in (rng.integers(0, P, P) for _ in range(args.n_iter))])
                    lo, hi = np.nanpercentile(bk, [2.5, 97.5])
                    rows.append(dict(seed=seed, space=space, field=fname, condition=cond, quantity="kappa", value=sir.kappa(obs, exp), ci_low=lo, ci_high=hi))
                r = sir.compare(mats[(fname, "stimulation")], mats[(fname, "sham")], M, np.random.default_rng(seed), args.n_iter, args.permutations, args.boot_perms)
                comp.append((space, fname, r))
                rows.append(dict(seed=seed, space=space, field=fname, condition="stimulation - sham", quantity="delta", value=r["delta"], ci_low=r["ci_low"], ci_high=r["ci_high"]))
                rows.append(dict(seed=seed, space=space, field=fname, condition="stimulation - sham", quantity="p", value=r["p_perm"], ci_low=np.nan, ci_high=np.nan))
        for space in spaces:
            ps = [(f, r["p_perm"]) for sp, f, r in comp if sp == space]
            q = sir.bh_fdr([p for _, p in ps])
            for (f, _), qq in zip(ps, q):
                rows.append(dict(seed=seed, space=space, field=f, condition="stimulation - sham", quantity="q", value=qq, ci_low=np.nan, ci_high=np.nan))
        print(f"seed {seed} done")
    # reported seed-42 results
    S, C = pd.read_csv(sir.OUT_DIR / "irr_summary.csv"), pd.read_csv(sir.OUT_DIR / "irr_comparison.csv")
    for r in S.itertuples():
        rows.append(dict(seed=42, space=r.space, field=r.field, condition=r.condition, quantity="kappa", value=r.semantic_kappa, ci_low=r.ci_low, ci_high=r.ci_high))
    for r in C.itertuples():
        for qn, v, lo, hi in (("delta", r.delta, r.ci_low, r.ci_high), ("p", r.p_perm, np.nan, np.nan), ("q", r.q_bh, np.nan, np.nan)):
            rows.append(dict(seed=42, space=r.space, field=r.field, condition="stimulation - sham", quantity=qn, value=v, ci_low=lo, ci_high=hi))
    seeds = pd.DataFrame(rows)
    seeds.to_csv(sir.OUT_DIR / "seed_stability.csv", index=False, float_format="%.6f")

    # ---- 2. agreement per tasting ----------------------------------------------------------------------------------------------
    M = spaces["centered (main)"]
    irows = []
    for fname in sir.FIELDS.values():
        for cond in sir.CONDITIONS:
            L = mats[(fname, cond)]
            P = L.shape[0]
            rng = np.random.default_rng(42)
            ids = np.arange(P)
            _, _, per = sir.pair_stats(L, M, ids)
            exp = sir.expected(L, M, ids, args.permutations, rng)
            boot = np.array([sir.pair_stats(L[bi], M, bi)[2] for bi in (rng.integers(0, P, P) for _ in range(args.n_iter))])
            for j, it in enumerate(items):
                k = (per[j] - exp) / (1 - exp)
                kb = (boot[:, j] - exp) / (1 - exp)
                irows.append(dict(field=fname, condition=cond, item=it, n_raters=int((L[:, j] >= 0).sum()), kappa=k, ci_low=np.nanpercentile(kb, 2.5), ci_high=np.nanpercentile(kb, 97.5)))
    items_df = pd.DataFrame(irows)
    items_df.to_csv(sir.OUT_DIR / "item_agreement.csv", index=False, float_format="%.6f")

    # ---- report ----------------------------------------------------------------------------------------------------------------
    md = ["# Robustness of the semantic IRR (exploratory)", "",
          f"Seed 42 is the reported analysis; seeds {', '.join(map(str, args.seeds))} repeat it with the same settings ({args.permutations} chance shuffles, {args.n_iter} bootstrap / swap iterations, "
          f"{args.boot_perms} chance shuffles inside each resample).", "", "## 1. Spread of each quantity across seeds", "",
          "| Space | Field | Condition | Quantity | Seed 42 (reported) | Min | Max | Range |", "|---|---|---|---|---:|---:|---:|---:|"]
    for (space, field, cond, qn), g in seeds.groupby(["space", "field", "condition", "quantity"], sort=False):
        v = g.set_index("seed")["value"]
        md.append(f"| {space} | {field} | {cond} | {qn} | {v.loc[42]:.3f} | {v.min():.3f} | {v.max():.3f} | {v.max() - v.min():.3f} |")
    for qn in ("kappa", "delta"):
        g = seeds[(seeds.quantity == qn)].groupby(["space", "field", "condition"])
        rng_ = g["value"].agg(lambda s: s.max() - s.min())
        lo_ = seeds[seeds.quantity == qn].groupby(["space", "field", "condition", "seed"])["ci_low"].first().groupby(level=[0, 1, 2]).agg(lambda s: s.max() - s.min())
        md += ["", f"Largest range across seeds for {qn}: point estimate {rng_.max():.4f}, lower interval limit {lo_.max():.4f}."]
    md += ["", "## 2. Semantic kappa per tasting (centered space; chance level of the whole condition; participant-bootstrap CI)", "",
           "| Field | Tasting | Stimulation | Sham |", "|---|---|---|---|"]
    for (field, it), g in items_df.groupby(["field", "item"], sort=False):
        g = g.set_index("condition")
        md.append(f"| {field} | {it} | {g.loc['stimulation','kappa']:.3f} [{g.loc['stimulation','ci_low']:.3f}, {g.loc['stimulation','ci_high']:.3f}] | "
                  f"{g.loc['sham','kappa']:.3f} [{g.loc['sham','ci_low']:.3f}, {g.loc['sham','ci_high']:.3f}] |")
    (sir.OUT_DIR / "robustness_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
