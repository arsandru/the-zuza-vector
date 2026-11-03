#!/usr/bin/env python3
"""Between-participant semantic agreement in the Qwen space centered on the descriptor mean (alternative embedding space, exploratory).

Same cleaned descriptors (main pipeline) and Qwen3-Embedding-0.6B with the aroma/flavor instruction as semantic_irr.py, but each embedding has
the mean descriptor embedding (weighted by occurrences, over both text fields) subtracted before rows are normalised and compared by cosine.
This removes the generic component shared by all coffee descriptors. No wheel, aliases or mapping are involved; centering is the only change.
Chance, semantic kappa, participant bootstrap CI, the paired stimulation vs sham comparison and BH-FDR q are those of semantic_irr.py and
compare_conditions.py. Outputs (irr/outputs/): centered_space_summary.csv, centered_space_comparison.csv, centered_space_report.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

import semantic_irr as sir
from compare_conditions import compare, kappa_of


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

    df = sir.load(sir.DEFAULT_INPUT)
    items = sorted(df["item"].unique())
    lab = {c: df[c].map(lambda x: None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)) for c in sir.FIELDS}
    uniq = sorted({v for c in sir.FIELDS for v in lab[c].dropna()})
    idx = {v: i for i, v in enumerate(uniq)}
    model = SentenceTransformer(args.model)
    E = unit_rows(np.asarray(model.encode([args.instruction + u for u in uniq], batch_size=16, show_progress_bar=False), dtype=float))
    occ = np.array([sum((lab[c] == u).sum() for c in sir.FIELDS) for u in uniq], dtype=float)
    Ec = unit_rows(E - np.average(E, axis=0, weights=occ))
    M = np.clip(np.einsum("ud,vd->uv", Ec, Ec), -1, 1)
    print(f"{len(uniq)} unique descriptors")

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
    sdf.to_csv(sir.OUT_DIR / "centered_space_summary.csv", index=False, float_format="%.6f")
    cdf.to_csv(sir.OUT_DIR / "centered_space_comparison.csv", index=False, float_format="%.6f")

    md = ["# Agreement in the centered Qwen space (exploratory)", "",
          f"{len(uniq)} unique cleaned descriptors; model {args.model}, instruction {args.instruction.strip()!r}; embeddings centered on the occurrence-weighted descriptor mean; "
          f"chance = {args.permutations} shuffles; CI and p = participant bootstrap / condition swap with {args.n_iter} iterations; seed {args.seed}.", "",
          "## Kappa per condition", "", "| Field | Condition | Descriptors | Observed | Expected | Kappa [95% CI] |", "|---|---|---:|---:|---:|---|"]
    md += [f"| {r.field} | {r.condition} | {r.n_descriptors} | {r.similarity_observed:.3f} | {r.similarity_expected:.3f} | {r.semantic_kappa:.3f} [{r.ci_low:.3f}, {r.ci_high:.3f}] |" for r in sdf.itertuples()]
    md += ["", "## Stimulation vs sham", "", "| Field | Stimulation | Sham | Delta [95% CI] | p | q (BH) |", "|---|---:|---:|---|---:|---:|"]
    md += [f"| {r.field} | {r.kappa_stimulation:.3f} | {r.kappa_sham:.3f} | {r.delta:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}] | {r.p_perm:.2f} | {r.q_bh:.2f} |" for r in cdf.itertuples()]
    (sir.OUT_DIR / "centered_space_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
