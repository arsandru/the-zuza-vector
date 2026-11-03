#!/usr/bin/env python3
"""Between-participant semantic agreement in a flavor-wheel space (alternative embedding space for the IRR; no descriptor aliases or mapping).

Space: the anchors are every term, category name and family name of the SCA flavor wheel (data/SCA flavor wheel.csv, nothing else; the wheel's
own family 5 label "other" is skipped). A cleaned descriptor (main pipeline, irr/semantic_irr.py) is embedded with Qwen3-Embedding-0.6B
(aroma/flavor instruction) and described by its cosine similarity to every anchor; each anchor coordinate is z-scored across all descriptor
occurrences (this also removes the generic component shared by all food words), and profiles are compared by cosine. The descriptor keeps its
own text: nothing is mapped to a wheel node and the alias file is not used. Anchors, standardisation and similarity are fixed in advance.
Agreement, chance (each participant's descriptors shuffled across the items of the condition), semantic kappa, participant bootstrap CI and
the paired stimulation vs sham comparison are those of semantic_irr.py and compare_conditions.py. BH-FDR q over the 2 fields.
Space check (wheel vocabulary only): for pairs of wheel terms, does similarity separate same-family (and same-category) pairs from other pairs?
The two terms of a pair are removed from the anchors before their profiles are computed. Compared with the plain Qwen space and the Qwen space
centered on the descriptor mean.
Outputs (irr/outputs/): wheel_space_summary.csv, wheel_space_comparison.csv, wheel_space_check.csv, wheel_space_report.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

import semantic_irr as sir
from compare_conditions import compare, kappa_of

sys.path.insert(0, str(sir.ROOT / "distribution"))
import wheel_mapping as wm  # noqa: E402  (only the wheel vocabulary is used, not the aliases)


def unit_rows(X):
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=sir.DEFAULT_MODEL)
    ap.add_argument("--instruction", default=sir.INSTRUCTION)
    ap.add_argument("--permutations", type=int, default=2000)
    ap.add_argument("--n-iter", type=int, default=1000)
    ap.add_argument("--boot-perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    nodes, _, _ = wm.build_vocab()
    anchor_nodes = [n for n in nodes if n != wm.OTHER and n != "5_other"]
    atext = sorted({nodes[n][1] for n in anchor_nodes})
    model = SentenceTransformer(args.model)

    def embed(texts):
        return unit_rows(np.asarray(model.encode([args.instruction + t for t in texts], batch_size=16, show_progress_bar=False), dtype=float))

    A = embed(atext)

    df = sir.load(sir.DEFAULT_INPUT)
    items = sorted(df["item"].unique())
    lab = {c: df[c].map(lambda x: None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)) for c in sir.FIELDS}
    uniq = sorted({v for c in sir.FIELDS for v in lab[c].dropna()})
    idx = {v: i for i, v in enumerate(uniq)}
    E = embed(uniq)
    occ = np.array([sum((lab[c] == u).sum() for c in sir.FIELDS) for u in uniq], dtype=float)
    S = np.einsum("ud,kd->uk", E, A)
    mu = np.average(S, axis=0, weights=occ)
    sd = np.sqrt(np.average((S - mu) ** 2, axis=0, weights=occ))
    V = unit_rows((S - mu) / np.maximum(sd, 1e-12))
    M = np.clip(np.einsum("ud,vd->uv", V, V), -1, 1)
    print(f"{len(atext)} anchors, {len(uniq)} unique descriptors")

    # ---- space check on wheel terms --------------------------------------------------------------------------------------------------
    leaves = [n for n in nodes if n.count("|") == 2]
    ltxt = [nodes[n][1] for n in leaves]
    L = embed(ltxt)
    fam = np.array([n.split("|")[0] for n in leaves])
    cat = np.array(["|".join(n.split("|")[:2]) for n in leaves])
    mu_e = np.average(E, axis=0, weights=occ)
    raw = np.einsum("id,jd->ij", L, L)
    Lc = unit_rows(L - mu_e)
    cen = np.einsum("id,jd->ij", Lc, Lc)
    SL = np.einsum("id,kd->ik", L, A)
    a_idx = {t: k for k, t in enumerate(atext)}
    pairs = [(i, j) for i in range(len(leaves)) for j in range(i + 1, len(leaves))]
    wheel_sim = []
    for i, j in pairs:
        keep = np.ones(len(atext), bool)
        keep[a_idx[ltxt[i]]] = keep[a_idx[ltxt[j]]] = False
        zi = (SL[i, keep] - mu[keep]) / np.maximum(sd[keep], 1e-12)
        zj = (SL[j, keep] - mu[keep]) / np.maximum(sd[keep], 1e-12)
        wheel_sim.append(float(zi @ zj / (np.linalg.norm(zi) * np.linalg.norm(zj))))
    same_f = np.array([fam[i] == fam[j] for i, j in pairs])
    same_c = np.array([cat[i] == cat[j] for i, j in pairs])
    check = []
    for name, sims in (("Qwen (plain)", [raw[i, j] for i, j in pairs]), ("Qwen (centered on descriptor mean)", [cen[i, j] for i, j in pairs]),
                       ("wheel space", wheel_sim)):
        sims = np.asarray(sims)
        check.append(dict(space=name, n_term_pairs=len(pairs), auc_same_family=roc_auc_score(same_f, sims), auc_same_category=roc_auc_score(same_c, sims),
                          mean_sim_same_family=sims[same_f].mean(), mean_sim_other=sims[~same_f].mean()))
    chk = pd.DataFrame(check)
    print(chk.round(3).to_string(index=False))

    # ---- IRR in the wheel space ----------------------------------------------------------------------------------------------------
    summ, comp = [], []
    for col, fname in sir.FIELDS.items():
        Ls = {}
        for cond in sir.CONDITIONS:
            sub = df[df["condition"] == cond].copy()
            sub["lbl"] = lab[col][sub.index]
            Ls[cond], _ = sir.label_matrix(sub, idx, items)
        for cond in sir.CONDITIONS:
            Lm = Ls[cond]
            P = Lm.shape[0]
            rng = np.random.default_rng(args.seed)
            ids = np.arange(P)
            obs = sir.pair_stats(Lm, M, ids)[0]
            exp = sir.expected(Lm, M, ids, args.permutations, rng)
            bk = np.empty(args.n_iter)
            for b in range(args.n_iter):
                bi = rng.integers(0, P, P)
                bk[b] = kappa_of(Lm[bi], M, bi, args.boot_perms, rng)
            lo, hi = np.nanpercentile(bk, [2.5, 97.5])
            summ.append(dict(field=fname, condition=cond, n_descriptors=int((Lm >= 0).sum()), similarity_observed=obs, similarity_expected=exp,
                             semantic_kappa=sir.kappa(obs, exp), ci_low=lo, ci_high=hi))
        r = compare(Ls["stimulation"], Ls["sham"], M, np.random.default_rng(args.seed), args.n_iter, args.permutations, args.boot_perms)
        comp.append(dict(field=fname, **r))
        print(f"{fname:12} stim {r['kappa_stimulation']:.3f} sham {r['kappa_sham']:.3f} delta {r['delta']:+.3f} [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] p = {r['p_perm']:.2f}")
    sdf, cdf = pd.DataFrame(summ), pd.DataFrame(comp)
    cdf["q_bh"] = sir.bh_fdr(cdf["p_perm"])
    sdf.to_csv(sir.OUT_DIR / "wheel_space_summary.csv", index=False, float_format="%.6f")
    cdf.to_csv(sir.OUT_DIR / "wheel_space_comparison.csv", index=False, float_format="%.6f")
    chk.to_csv(sir.OUT_DIR / "wheel_space_check.csv", index=False, float_format="%.6f")

    md = ["# Agreement in a flavor-wheel space (exploratory)", "",
          f"{len(atext)} wheel anchors (terms, category names, family names), {len(uniq)} unique cleaned descriptors; model {args.model}; chance = {args.permutations} shuffles; "
          f"CI and p = participant bootstrap / condition swap with {args.n_iter} iterations; seed {args.seed}.", "",
          "## Space check on wheel terms (the two terms of a pair are removed from the anchors)", "",
          "| Space | Term pairs | AUC same family | AUC same category | Mean sim. same family | Mean sim. other |", "|---|---:|---:|---:|---:|---:|"]
    md += [f"| {r.space} | {r.n_term_pairs} | {r.auc_same_family:.3f} | {r.auc_same_category:.3f} | {r.mean_sim_same_family:.3f} | {r.mean_sim_other:.3f} |" for r in chk.itertuples()]
    md += ["", "## Kappa per condition", "", "| Field | Condition | Descriptors | Observed | Expected | Kappa [95% CI] |", "|---|---|---:|---:|---:|---|"]
    md += [f"| {r.field} | {r.condition} | {r.n_descriptors} | {r.similarity_observed:.3f} | {r.similarity_expected:.3f} | {r.semantic_kappa:.3f} [{r.ci_low:.3f}, {r.ci_high:.3f}] |" for r in sdf.itertuples()]
    md += ["", "## Stimulation vs sham", "", "| Field | Stimulation | Sham | Delta [95% CI] | p | q (BH) |", "|---|---:|---:|---|---:|---:|"]
    md += [f"| {r.field} | {r.kappa_stimulation:.3f} | {r.kappa_sham:.3f} | {r.delta:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}] | {r.p_perm:.2f} | {r.q_bh:.2f} |" for r in cdf.itertuples()]
    (sir.OUT_DIR / "wheel_space_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
