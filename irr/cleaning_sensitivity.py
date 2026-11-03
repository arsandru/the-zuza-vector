#!/usr/bin/env python3
"""Does the text cleaning or the embedding model drive the stimulation vs sham comparison? (sensitivity, exploratory)

Repeats the paired comparison of compare_conditions.py (delta = kappa(stimulation) - kappa(sham), paired participant bootstrap CI,
condition-swap permutation p) for
 - Qwen3-Embedding-0.6B (aroma/flavor instruction) under cleaning variants: raw (lowercase only), spelling only, lemma only, stop words
   only, lemma + stop words, canonical synonym variants only, full pipeline (the default), and full pipeline + descriptors only (drops comparison, intensity,
   evaluation and mouthfeel words; descriptors left empty become missing);
 - bge-small-en-v1.5 and all-mpnet-base-v2 (no instruction) with raw, full and full + descriptors only.
Output: irr/outputs/cleaning_sensitivity.csv, cleaning_sensitivity.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

import semantic_irr as sir
from compare_conditions import compare

VARIANTS = {
    "raw": dict(spelling=False, lemma=False, stop=False, canon=False),
    "spelling only": dict(spelling=True, lemma=False, stop=False, canon=False),
    "lemma only": dict(spelling=False, lemma=True, stop=False, canon=False),
    "stop words only": dict(spelling=False, lemma=False, stop=True, canon=False),
    "synonym variants only": dict(spelling=False, lemma=False, stop=False, canon=True),
    "lemma + stop words": dict(spelling=False, lemma=True, stop=True, canon=False),
    "full": dict(spelling=True, lemma=True, stop=True, canon=True),
    "full + descriptors only": dict(spelling=True, lemma=True, stop=True, canon=True, descriptors_only=True),
}
RUNS = [(sir.DEFAULT_MODEL, v) for v in VARIANTS] + [(m, v) for m in ("BAAI/bge-small-en-v1.5", "sentence-transformers/all-mpnet-base-v2") for v in ("raw", "full", "full + descriptors only")]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n-iter", type=int, default=1000)
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--boot-perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    df = sir.load(sir.DEFAULT_INPUT)
    items = sorted(df["item"].unique())
    models, rows = {}, []
    for mname, vname in RUNS:
        flags = VARIANTS[vname]
        lab = {c: df[c].map(lambda x: None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x, **flags)) for c in sir.FIELDS}
        uniq = sorted({v for c in sir.FIELDS for v in lab[c].dropna()})
        idx = {v: i for i, v in enumerate(uniq)}
        if mname not in models:
            models[mname] = SentenceTransformer(mname)
        prefix = sir.INSTRUCTION if mname == sir.DEFAULT_MODEL else ""
        E = np.asarray(models[mname].encode([prefix + u for u in uniq], batch_size=16, show_progress_bar=False), dtype=float)
        E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
        M = np.clip(np.einsum("id,jd->ij", E, E), -1, 1)
        for col, fname in sir.FIELDS.items():
            Ls = {}
            for cond in sir.CONDITIONS:
                sub = df[df["condition"] == cond].copy()
                sub["lbl"] = lab[col][sub.index]
                Ls[cond], _ = sir.label_matrix(sub, idx, items)
            r = compare(Ls["stimulation"], Ls["sham"], M, np.random.default_rng(args.seed), args.n_iter, args.perms, args.boot_perms)
            rows.append(dict(model=mname.split("/")[-1], cleaning=vname, field=fname, n_unique=len(uniq), **r))
            print(f"{mname.split('/')[-1]:>20} {vname:22} {fname:13} stim {r['kappa_stimulation']:.3f} sham {r['kappa_sham']:.3f} "
                  f"delta {r['delta']:+.3f} [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] p = {r['p_perm']:.2f}")
    res = pd.DataFrame(rows)
    res.to_csv(sir.OUT_DIR / "cleaning_sensitivity.csv", index=False, float_format="%.6f")
    md = ["# Cleaning and model sensitivity of the stimulation vs sham comparison (exploratory)", "",
          f"Paired participant bootstrap ({args.n_iter}) and condition-swap permutation ({args.n_iter}); seed {args.seed}.", "",
          "| Model | Cleaning | Field | Unique descriptors | Stimulation | Sham | Delta [95% CI] | p |", "|---|---|---|---:|---:|---:|---|---:|"]
    for _, r in res.iterrows():
        md.append(f"| {r.model} | {r.cleaning} | {r.field} | {int(r.n_unique)} | {r.kappa_stimulation:.3f} | {r.kappa_sham:.3f} | "
                  f"{r.delta:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}] | {r.p_perm:.2f} |")
    (sir.OUT_DIR / "cleaning_sensitivity.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
