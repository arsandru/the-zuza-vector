#!/usr/bin/env python3
"""Stimulation vs sham: difference in between-participant semantic kappa (exploratory).

Same pipeline as semantic_irr.py (cleaning, Qwen3-Embedding-0.6B with the aroma/flavor instruction, kappa per condition and field).
Statistic: delta = kappa(stimulation) - kappa(sham), per text field. Every participant contributes to both conditions, so
 - CI: paired participant bootstrap (the same resampled participants in both conditions; kappa recomputed, expected similarity with
   `--boot-perms` shuffles).
 - p: per participant, the stimulation and sham descriptor sets are swapped with probability 1/2 (condition labels exchangeable under
   no condition effect within participant); two-sided permutation p with the same kappa recomputation.
Two fields = two tests; Holm-adjusted p is reported. Outputs: irr/outputs/condition_comparison.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import semantic_irr as sir


def kappa_of(L, M, ids, n_perm, rng):
    return sir.kappa(sir.pair_stats(L, M, ids)[0], sir.expected(L, M, ids, n_perm, rng))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=sir.DEFAULT_INPUT)
    ap.add_argument("--model", default=sir.DEFAULT_MODEL)
    ap.add_argument("--instruction", default=sir.INSTRUCTION)
    ap.add_argument("--n-iter", type=int, default=2000, help="bootstrap and permutation iterations")
    ap.add_argument("--perms", type=int, default=2000, help="shuffles for the observed expected similarity")
    ap.add_argument("--boot-perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    df = sir.load(args.input)
    items = sorted(df["item"].unique())
    for col in sir.FIELDS:
        df[col + "_lbl"] = df[col].map(lambda x: None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x))
    uniq = sorted({v for col in sir.FIELDS for v in df[col + "_lbl"].dropna()})
    emb_index = {v: i for i, v in enumerate(uniq)}
    E = np.asarray(SentenceTransformer(args.model).encode([args.instruction + u for u in uniq], batch_size=16, show_progress_bar=False), dtype=float)
    E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
    M = np.clip(np.einsum("id,jd->ij", E, E), -1, 1)

    rows = []
    for col, fname in sir.FIELDS.items():
        Ls = {}
        for cond in sir.CONDITIONS:
            sub = df[df["condition"] == cond].copy()
            sub["lbl"] = sub[col + "_lbl"]
            Ls[cond], parts = sir.label_matrix(sub, emb_index, items)
            if cond == sir.CONDITIONS[0]:
                p0 = parts
            assert parts == p0, "participants differ between conditions"
        A, B = Ls["stimulation"], Ls["sham"]
        P = len(p0)
        ids = np.arange(P)
        rng = np.random.default_rng(args.seed)
        ka, kb = kappa_of(A, M, ids, args.perms, rng), kappa_of(B, M, ids, args.perms, rng)
        d_obs = ka - kb
        boot = np.empty(args.n_iter)
        for b in range(args.n_iter):
            idx = rng.integers(0, P, P)
            boot[b] = kappa_of(A[idx], M, idx, args.boot_perms, rng) - kappa_of(B[idx], M, idx, args.boot_perms, rng)
        null = np.empty(args.n_iter)
        for b in range(args.n_iter):
            sw = rng.random(P) < 0.5
            A2, B2 = np.where(sw[:, None], B, A), np.where(sw[:, None], A, B)
            null[b] = kappa_of(A2, M, ids, args.boot_perms, rng) - kappa_of(B2, M, ids, args.boot_perms, rng)
        p = (1 + (np.abs(null) >= abs(d_obs) - 1e-12).sum()) / (1 + args.n_iter)
        lo, hi = np.nanpercentile(boot, [2.5, 97.5])
        rows.append(dict(field=fname, n_participants=P, kappa_stimulation=ka, kappa_sham=kb, delta=d_obs, ci_low=lo, ci_high=hi, p_perm=p))
        print(f"{fname:13} stim {ka:.3f}  sham {kb:.3f}  delta {d_obs:+.3f} [{lo:+.3f}, {hi:+.3f}]  p = {p:.3f}")
    res = pd.DataFrame(rows)
    order = res["p_perm"].argsort().to_numpy()
    adj = np.empty(len(res))
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(res) - rank) * res["p_perm"].iloc[i]))
        adj[i] = run
    res["p_holm"] = adj
    res.to_csv(sir.OUT_DIR / "condition_comparison.csv", index=False, float_format="%.6f")
    print(res.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
