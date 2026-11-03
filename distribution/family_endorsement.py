#!/usr/bin/env python3
"""Do stimulation and sham endorse different SCA wheel-family profiles? (main analysis of distribution/, exploratory)

Check-all-that-apply design: every participant tasted 2 coffees x 3 repeated tastings in each condition and wrote an aroma descriptor and a
flavor descriptor per tasting. A descriptor is cleaned and mapped to wheel nodes (irr/semantic_irr.py main pipeline, wheel_mapping.py;
words with no wheel home -> `5_other`, which is also wheel family 5) and a family is *endorsed* at a tasting if any of its nodes is present.
A tasting without a descriptor ("n\\a", empty) is missing, not "not endorsed".
Unit = participant. Per participant, condition, field and family: endorsement rate = endorsed / non-missing tastings. Paired difference
d = rate(stimulation) - rate(sham); participants without a non-missing tasting in both conditions are left out of that field.

 1. Omnibus (per field): T = sum over the 9 families of t^2, t = mean(d) / (sd(d)/sqrt(n)). Null: every participant's difference vector is
    sign-flipped with probability 1/2 (= swapping that participant's stimulation and sham labels), n = --n-perm; p = (1 + #{T* >= T}) / (1 + n-perm).
 2. Per family: mean difference in endorsement rate with a participant-bootstrap 95% CI; unadjusted sign-flip p; max-|t| adjusted p over all
    families of both fields together (same flips for a participant in both fields; strong control of the family-wise error rate).
 3. Does the condition effect vary across the 3 tastings? Per participant and tasting, d_r = rate difference (needs a non-missing tasting in both
    conditions at every r). Statistic: sum over families of the repeated-measures F of d_r across r; null: tasting labels permuted within participant.
Outputs (distribution/outputs/): family_endorsement.csv, family_endorsement_omnibus.csv, family_endorsement_by_tasting.csv, family_endorsement_report.md
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import wheel_mapping as wm

sir = wm.sir
OUT_DIR = Path(__file__).resolve().parent / "outputs"


def tstats(D: np.ndarray) -> np.ndarray:
    """D: participants x families with NaN = excluded; paired t per family."""
    n = np.sum(~np.isnan(D), axis=0)
    m = np.nanmean(D, axis=0)
    sd = np.nanstd(D, axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = m / (sd / np.sqrt(n))
    return np.where(np.isfinite(t), t, 0.0)


def rm_F(X: np.ndarray) -> np.ndarray:
    """X: participants x tastings x families (complete); repeated-measures F of the tasting effect per family."""
    n, r, _ = X.shape
    gm = X.mean(axis=(0, 1), keepdims=True)
    ss_t = n * ((X.mean(axis=0, keepdims=True) - gm) ** 2).sum(axis=1)[0]
    ss_s = r * ((X.mean(axis=1, keepdims=True) - gm) ** 2).sum(axis=(0, 1))
    ss_e = ((X - gm) ** 2).sum(axis=(0, 1)) - ss_t - ss_s
    with np.errstate(divide="ignore", invalid="ignore"):
        F = (ss_t / (r - 1)) / (ss_e / ((n - 1) * (r - 1)))
    return np.where(np.isfinite(F), F, 0.0)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-perm", type=int, default=10000)
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    nodes, auto, _ = wm.build_vocab()
    amap = wm.load_aliases(nodes)
    fams = sorted(n for n in nodes if "|" not in n)
    fname = {f: ("other (5, incl. unmapped words)" if f == wm.OTHER else nodes[f][1]) for f in fams}
    df = sir.load(sir.DEFAULT_INPUT)
    subjects = sorted(df["subject"].unique())
    reps = sorted(df["repeated_ratings"].unique())
    P, R = len(subjects), len(reps)
    si = {s: i for i, s in enumerate(subjects)}
    ci = {c: i for i, c in enumerate(sir.CONDITIONS)}

    # arrays: endorsed[field][participant, condition, tasting(r), coffee] summed later; cnt = non-missing tastings
    D_all, names, Dr = {}, {}, {}
    for col, field in sir.FIELDS.items():
        end = np.zeros((P, 2, R, len(fams)))
        cnt = np.zeros((P, 2, R))
        for row in df.itertuples():
            x = df.at[row.Index, col]
            if pd.isna(x) or not str(x).strip():
                continue
            cl = sir.clean_descriptor(x)
            if cl is None:
                continue
            ns = wm.map_words(cl, auto, amap, True)[0]
            if not ns:
                continue
            i, c, r = si[row.subject], ci[row.condition], reps.index(row.repeated_ratings)
            cnt[i, c, r] += 1
            for f in {n.split("|")[0] for n in ns}:
                end[i, c, r, fams.index(f)] += 1
        tot_n, tot_e = cnt.sum(axis=2), end.sum(axis=2)  # participant x condition (x family)
        with np.errstate(divide="ignore", invalid="ignore"):
            rate = tot_e / tot_n[..., None]
        ok = (tot_n > 0).all(axis=1)
        d = np.where(ok[:, None], rate[:, 0, :] - rate[:, 1, :], np.nan)
        D_all[field] = (d, rate)
        with np.errstate(divide="ignore", invalid="ignore"):
            rr = end / cnt[..., None]
        dr = rr[:, 0] - rr[:, 1]  # participant x tasting x family
        Dr[field] = dr[~np.isnan(dr).any(axis=(1, 2))]
        print(f"{field}: {int(ok.sum())} participants with a non-missing tasting in both conditions; {len(Dr[field])} with all 3 tastings in both")

    fields = list(D_all)
    big = np.concatenate([D_all[f][0] for f in fields], axis=1)  # participants x (fields*families)
    t_obs = tstats(big)
    flips = rng.random((args.n_perm, P)) < 0.5
    t_null = np.empty((args.n_perm, big.shape[1]))
    for b in range(args.n_perm):
        t_null[b] = tstats(np.where(flips[b][:, None], -big, big))
    p_unadj = (1 + (np.abs(t_null) >= np.abs(t_obs) - 1e-12).sum(axis=0)) / (1 + args.n_perm)
    maxt = np.abs(t_null).max(axis=1)
    p_max = (1 + (maxt[:, None] >= np.abs(t_obs) - 1e-12).sum(axis=0)) / (1 + args.n_perm)

    rows, om = [], []
    nf = len(fams)
    for k, field in enumerate(fields):
        d, rate = D_all[field]
        sl = slice(k * nf, (k + 1) * nf)
        ok = ~np.isnan(d).any(axis=1)
        n = int(ok.sum())
        bo = np.empty((args.n_boot, nf))
        dd = d[ok]
        for b in range(args.n_boot):
            bo[b] = dd[rng.integers(0, n, n)].mean(axis=0)
        lo, hi = np.percentile(bo, [2.5, 97.5], axis=0)
        for j, f in enumerate(fams):
            rows.append(dict(field=field, family=fname[f], n=n, rate_stimulation=np.nanmean(rate[ok, 0, j]), rate_sham=np.nanmean(rate[ok, 1, j]),
                             diff=dd[:, j].mean(), ci_low=lo[j], ci_high=hi[j], t=t_obs[sl][j], p_unadj=p_unadj[sl][j], p_maxT=p_max[sl][j]))
        T = float((t_obs[sl] ** 2).sum())
        Tn = (t_null[:, sl] ** 2).sum(axis=1)
        om.append(dict(field=field, n=n, T=T, null_mean=Tn.mean(), null_p95=np.percentile(Tn, 95), p_perm=(1 + (Tn >= T - 1e-12).sum()) / (1 + args.n_perm)))
    res, omn = pd.DataFrame(rows), pd.DataFrame(om)
    lo_i, hi_i = omn["p_perm"].idxmin(), omn["p_perm"].idxmax()  # Holm over the 2 fields
    omn["p_holm"] = np.nan
    omn.loc[lo_i, "p_holm"] = min(1.0, 2 * omn.loc[lo_i, "p_perm"])
    omn.loc[hi_i, "p_holm"] = max(omn.loc[hi_i, "p_perm"], omn.loc[lo_i, "p_holm"]) if lo_i != hi_i else omn.loc[lo_i, "p_holm"]

    # tasting interaction
    ints, bt = [], []
    for field in fields:
        X = Dr[field]
        n = len(X)
        F = rm_F(X)
        S = float(F.sum())
        Sn = np.empty(args.n_perm)
        for b in range(args.n_perm):
            perm = np.argsort(rng.random((n, R)), axis=1)
            Sn[b] = rm_F(np.take_along_axis(X, perm[:, :, None], axis=1)).sum()
        ints.append(dict(field=field, n=n, sum_F=S, null_mean=Sn.mean(), null_p95=np.percentile(Sn, 95), p_perm=(1 + (Sn >= S - 1e-12).sum()) / (1 + args.n_perm)))
        for j, f in enumerate(fams):
            for r in range(R):
                bt.append(dict(field=field, family=fname[f], tasting=reps[r], n=n, mean_diff=X[:, r, j].mean()))
    ints, bt = pd.DataFrame(ints), pd.DataFrame(bt)

    OUT_DIR.mkdir(exist_ok=True)
    res.to_csv(OUT_DIR / "family_endorsement.csv", index=False, float_format="%.6f")
    omn.to_csv(OUT_DIR / "family_endorsement_omnibus.csv", index=False, float_format="%.6f")
    ints.to_csv(OUT_DIR / "family_endorsement_interaction.csv", index=False, float_format="%.6f")
    bt.to_csv(OUT_DIR / "family_endorsement_by_tasting.csv", index=False, float_format="%.6f")

    md = ["# Family endorsement, stimulation vs sham (exploratory)", "",
          f"Participants = unit; {args.n_perm} sign-flip permutations, {args.n_boot} bootstrap draws, seed {args.seed}. Rates are endorsements per non-missing tasting.", "",
          "## Omnibus (sum of squared paired t over the 9 families)", "", "| Field | n | T | Null mean (p95) | p | Holm p |", "|---|---:|---:|---|---:|---:|"]
    md += [f"| {r.field} | {r.n} | {r.T:.2f} | {r.null_mean:.2f} ({r.null_p95:.2f}) | {r.p_perm:.3f} | {r.p_holm:.3f} |" for r in omn.itertuples()]
    md += ["", "## Per family (difference = stimulation - sham, endorsement rate)", "", "| Field | Family | Stimulation | Sham | Difference [95% CI] | t | p | p (max-t, 18 tests) |", "|---|---|---:|---:|---|---:|---:|---:|"]
    md += [f"| {r.field} | {r.family} | {r.rate_stimulation:.2f} | {r.rate_sham:.2f} | {r.diff:+.2f} [{r.ci_low:+.2f}, {r.ci_high:+.2f}] | {r.t:+.2f} | {r.p_unadj:.3f} | {r.p_maxT:.3f} |"
           for r in res.itertuples()]
    md += ["", "## Does the condition effect vary across tastings? (sum over families of the repeated-measures F)", "", "| Field | n | sum F | Null mean (p95) | p |", "|---|---:|---:|---|---:|"]
    md += [f"| {r.field} | {r.n} | {r.sum_F:.2f} | {r.null_mean:.2f} ({r.null_p95:.2f}) | {r.p_perm:.3f} |" for r in ints.itertuples()]
    (OUT_DIR / "family_endorsement_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
