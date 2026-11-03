#!/usr/bin/env python3
"""Does the semantic IRR test approximately the same thing as the numeric ICC of the draft? (check, exploratory)

Draft ("October 2026 draft-3.md", section 3.5): ICC(A,1) of the overall rating, two-way random effects, absolute agreement of single ratings, targets =
coffee x repeated rating (6 per condition), raters = participants, separately under sham and stimulation, REML for the incomplete crossed design.
Reported: sham 0.134 [0.027, 0.261], stimulation 0.091 [0.009, 0.209], difference -0.043.

1. Replication: the same ICC on data/tDCS.csv (REML, crossed random effects target + rater, numpy/scipy; sigma2_target / (sigma2_target + sigma2_rater +
   sigma2_residual); the consistency version ICC(C,1) = sigma2_target / (sigma2_target + sigma2_residual) is added). CIs here are participant bootstraps
   (the draft's come from the intraclass package), so intervals are compared qualitatively. Also run for fragrance (aroma) and flavour (flavor).
2. Semantic analogues on the same design (centered space, cleaned descriptors, as semantic_irr.py):
   - consistency analogue = the main semantic kappa: chance = each participant's descriptors shuffled across the items of the condition (removes each
     participant's own vocabulary habit, as ICC(C,1) removes each rater's own scale use);
   - absolute-agreement analogue: chance = all descriptors of the condition shuffled across participants and items (a participant's habitual vocabulary
     counts as disagreement, as in ICC(A,1)). In the centered space this is (within-target mean similarity - all-pairs mean similarity) / (1 - all-pairs
     mean similarity), the vector version of the share of variance that is between targets.
3. Pair-level link: for pairs of participants rating the same tasting, is a smaller numeric difference accompanied by a more similar descriptor? Spearman
   correlation between |score difference| and descriptor similarity (aroma notes vs fragrance, flavor notes vs flavour, both vs overall), participant bootstrap CI.
Outputs (irr/outputs/): numeric_check_icc.csv, numeric_check_pairs.csv, numeric_check_report.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import rankdata

import semantic_irr as sir

NUM = {"overall": "overall", "fragrance": "fragrance", "flavour": "flavour"}
PAIR = [("notesaroma", "fragrance"), ("flavor_notes", "flavour"), ("notesaroma", "overall"), ("flavor_notes", "overall")]
DRAFT = {"sham": (0.134, 0.027, 0.261), "stimulation": (0.091, 0.009, 0.209)}


def numeric(df, col):
    return pd.to_numeric(df[col].astype(str).str.replace(",", "."), errors="coerce")


def reml_icc(y, tg, rg):
    """REML variance components of y = mu + target + rater + error (crossed random effects) -> (ICC(A,1), ICC(C,1), components)."""
    keep = ~np.isnan(y)
    y, tg, rg = y[keep], tg[keep], rg[keep]
    n = len(y)
    Zt = (tg[:, None] == np.unique(tg)[None, :]).astype(float)
    Zr = (rg[:, None] == np.unique(rg)[None, :]).astype(float)
    Kt, Kr = np.einsum("ij,kj->ik", Zt, Zt), np.einsum("ij,kj->ik", Zr, Zr)  # einsum: spurious matmul overflow warnings here
    one = np.ones((n, 1))

    def nll(lv):
        st, sr, se = np.exp(lv)
        V = st * Kt + sr * Kr + se * np.eye(n)
        L = np.linalg.cholesky(V)
        Vi1 = np.linalg.solve(V, one)
        xtvx = float(Vi1.sum())
        Viy = np.linalg.solve(V, y)
        yPy = float(np.einsum("i,i->", y, Viy) - Viy.sum() ** 2 / xtvx)
        return 0.5 * (2 * np.log(np.diag(L)).sum() + np.log(xtvx) + yPy)

    v0 = np.var(y)
    best = None
    for start in (np.log([0.3 * v0, 0.3 * v0, 0.4 * v0]), np.log([0.05 * v0, 0.5 * v0, 0.4 * v0])):
        r = minimize(nll, start, method="L-BFGS-B", bounds=[(-12, 6)] * 3)
        if best is None or r.fun < best.fun:
            best = r
    st, sr, se = np.exp(best.x)
    return st / (st + sr + se), st / (st + se), (st, sr, se)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--pair-boot", type=int, default=500)
    ap.add_argument("--permutations", type=int, default=2000)
    ap.add_argument("--boot-perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    df = sir.load(sir.DEFAULT_INPUT)
    items = sorted(df["item"].unique())
    subs = sorted(df["subject"].unique())
    rng = np.random.default_rng(args.seed)
    rows = []

    # ---- 1. numeric ICC ----------------------------------------------------------------------------------------------------------
    for name, col in NUM.items():
        df["_y"] = numeric(df, col)
        est = {}
        for cond in sir.CONDITIONS:
            sub = df[df["condition"] == cond]
            y, tg, rg = sub["_y"].to_numpy(), sub["item"].to_numpy(), sub["subject"].to_numpy()
            ia, ic, comp = reml_icc(y, tg, rg)
            boots = []
            for _ in range(args.n_boot):
                pick = rng.integers(0, len(subs), len(subs))
                parts = [sub[sub["subject"] == subs[i]].assign(subject=f"{subs[i]}_{k}") for k, i in enumerate(pick)]
                b = pd.concat(parts)
                boots.append(reml_icc(b["_y"].to_numpy(), b["item"].to_numpy(), b["subject"].to_numpy())[:2])
            boots = np.array(boots)
            lo, hi = np.percentile(boots, [2.5, 97.5], axis=0)
            est[cond] = (ia, ic, boots)
            rows.append(dict(kind="numeric", measure=name, version="ICC(A,1) absolute agreement", condition=cond, value=ia, ci_low=lo[0], ci_high=hi[0], n_missing=int(sub["_y"].isna().sum())))
            rows.append(dict(kind="numeric", measure=name, version="ICC(C,1) consistency", condition=cond, value=ic, ci_low=lo[1], ci_high=hi[1], n_missing=int(sub["_y"].isna().sum())))
        for v, k in (("ICC(A,1) absolute agreement", 0), ("ICC(C,1) consistency", 1)):
            d = est["stimulation"][2][:, k] - est["sham"][2][:, k]
            rows.append(dict(kind="numeric", measure=name, version=v, condition="stimulation - sham", value=est["stimulation"][k] - est["sham"][k],
                             ci_low=np.percentile(d, 2.5), ci_high=np.percentile(d, 97.5)))
            print(f"numeric {name:9} {v:28} sham {est['sham'][k]:.3f} stim {est['stimulation'][k]:.3f} diff {est['stimulation'][k] - est['sham'][k]:+.3f}")

    # ---- 2. semantic analogues ----------------------------------------------------------------------------------------------------
    lab = {c: df[c].map(lambda x: None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)) for c in sir.FIELDS}
    uniq = sorted({v for c in sir.FIELDS for v in lab[c].dropna()})
    idx = {v: i for i, v in enumerate(uniq)}
    E = sir.unit_rows(np.asarray(SentenceTransformer(sir.DEFAULT_MODEL).encode([sir.INSTRUCTION + u for u in uniq], batch_size=16, show_progress_bar=False), dtype=float))
    occ = np.array([sum((lab[c] == u).sum() for c in sir.FIELDS) for u in uniq], dtype=float)
    Ec = sir.unit_rows(E - np.average(E, axis=0, weights=occ))
    M = np.clip(np.einsum("ud,vd->uv", Ec, Ec), -1, 1)

    def exp_pooled(L, ids, n_perm, r):
        vals = np.empty(n_perm)
        for b in range(n_perm):
            vals[b] = sir.pair_stats(r.permutation(L.ravel()).reshape(L.shape), M, ids)[0]
        return vals.mean()

    def k_pooled(L, ids, n_perm, r):
        o = sir.pair_stats(L, M, ids)[0]
        e = exp_pooled(L, ids, n_perm, r)
        return (o - e) / (1 - e)

    mats = {}
    for col, fname in sir.FIELDS.items():
        Ls = {}
        for cond in sir.CONDITIONS:
            sub = df[df["condition"] == cond].copy()
            sub["lbl"] = lab[col][sub.index]
            Ls[cond], _ = sir.label_matrix(sub, idx, items)
        mats[fname] = Ls
        res = {}
        for version, fn in (("consistency analogue (main semantic kappa)", lambda L, ids, r, n: sir.kappa_of(L, M, ids, n, r)),
                            ("absolute-agreement analogue (pooled chance)", lambda L, ids, r, n: k_pooled(L, ids, n, r))):
            est, boots = {}, {}
            for cond in sir.CONDITIONS:
                L = Ls[cond]
                P = L.shape[0]
                est[cond] = fn(L, np.arange(P), rng, args.permutations)
            bd = {c: [] for c in sir.CONDITIONS}
            for _ in range(args.n_boot):
                pick = rng.integers(0, len(subs), len(subs))
                for cond in sir.CONDITIONS:
                    bd[cond].append(fn(Ls[cond][pick], pick, rng, args.boot_perms))
            for cond in sir.CONDITIONS:
                lo, hi = np.percentile(bd[cond], [2.5, 97.5])
                rows.append(dict(kind="semantic", measure=fname, version=version, condition=cond, value=est[cond], ci_low=lo, ci_high=hi))
            d = np.array(bd["stimulation"]) - np.array(bd["sham"])
            rows.append(dict(kind="semantic", measure=fname, version=version, condition="stimulation - sham", value=est["stimulation"] - est["sham"],
                             ci_low=np.percentile(d, 2.5), ci_high=np.percentile(d, 97.5)))
            print(f"semantic {fname:12} {version:44} sham {est['sham']:.3f} stim {est['stimulation']:.3f} diff {est['stimulation'] - est['sham']:+.3f}")
    icc = pd.DataFrame(rows)
    icc.to_csv(sir.OUT_DIR / "numeric_check_icc.csv", index=False, float_format="%.6f")

    # ---- 3. pair-level link between numeric agreement and descriptor similarity --------------------------------------------------
    prow = []
    for fname, ncol in PAIR:
        df["_y"] = numeric(df, ncol)
        recs = []
        for cond in sir.CONDITIONS:
            sub = df[df["condition"] == cond]
            Y = np.full((len(subs), len(items)), np.nan)
            for r in sub.itertuples():
                Y[subs.index(r.subject), items.index(r.item)] = df.at[r.Index, "_y"]
            L = mats[fname][cond]
            for j in range(len(items)):
                ok = np.nonzero((L[:, j] >= 0) & ~np.isnan(Y[:, j]))[0]
                for a in range(len(ok)):
                    for b in range(a + 1, len(ok)):
                        p, q = ok[a], ok[b]
                        recs.append((p, q, abs(Y[p, j] - Y[q, j]), M[L[p, j], L[q, j]]))
        R = np.array(recs)

        def spear(Rm, w=None):
            x, y = Rm[:, 2], Rm[:, 3]
            return np.corrcoef(rankdata(x), rankdata(y))[0, 1]

        rho = spear(R)
        bs = []
        for _ in range(args.pair_boot):
            c = np.bincount(rng.integers(0, len(subs), len(subs)), minlength=len(subs))
            w = (c[R[:, 0].astype(int)] * c[R[:, 1].astype(int)]).astype(int)
            bs.append(spear(np.repeat(R, w, axis=0)))
        prow.append(dict(descriptor_field=fname, score=ncol, n_pairs=len(R), spearman_rho=rho, ci_low=np.percentile(bs, 2.5), ci_high=np.percentile(bs, 97.5)))
        print(f"pairs {fname:12} vs |diff {ncol}|: n = {len(R)}, rho = {rho:+.3f} [{prow[-1]['ci_low']:+.3f}, {prow[-1]['ci_high']:+.3f}]")
    pdf = pd.DataFrame(prow)
    pdf.to_csv(sir.OUT_DIR / "numeric_check_pairs.csv", index=False, float_format="%.6f")

    md = ["# Numeric ICC vs semantic IRR: do they test the same thing? (check, exploratory)", "",
          "Draft numbers (overall rating, ICC(A,1), REML): sham 0.134 [0.027, 0.261], stimulation 0.091 [0.009, 0.209], difference -0.043.", "",
          "## Agreement per condition and its stimulation - sham difference", "", "| Kind | Measure | Version | Sham | Stimulation | Stimulation - sham [95% bootstrap CI] |", "|---|---|---|---|---|---|"]
    for (kind, meas, ver), g in icc.groupby(["kind", "measure", "version"], sort=False):
        g = g.set_index("condition")
        f = lambda c: f"{g.loc[c, 'value']:.3f} [{g.loc[c, 'ci_low']:.3f}, {g.loc[c, 'ci_high']:.3f}]"
        md.append(f"| {kind} | {meas} | {ver} | {f('sham')} | {f('stimulation')} | {g.loc['stimulation - sham', 'value']:+.3f} [{g.loc['stimulation - sham', 'ci_low']:+.3f}, {g.loc['stimulation - sham', 'ci_high']:+.3f}] |")
    md += ["", "## Pair level: numeric difference vs descriptor similarity (same tasting, two participants)", "",
           "| Descriptor field | Score | Pairs | Spearman rho [95% participant-bootstrap CI] |", "|---|---|---:|---|"]
    md += [f"| {r.descriptor_field} | |score difference| {r.score} | {r.n_pairs} | {r.spearman_rho:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}] |" for r in pdf.itertuples()]
    (sir.OUT_DIR / "numeric_check_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
