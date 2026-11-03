#!/usr/bin/env python3
"""Agreement after mapping descriptors to the SCA flavor wheel vocabulary (alternative pipeline, exploratory).

Main pipeline (semantic_irr.clean_descriptor) -> each cleaned word is mapped to one wheel node:
 1. wheel terms (data/SCA flavor wheel.csv): level-3 terms and level-2 category names, cleaned with the same pipeline; longest match first
    (up to 3 words, e.g. "dark chocolate", "brown sugar"); a wheel term whose cleaning drops a word (e.g. "under ripe") is not matched
    automatically;
 2. aliases (data/sca_aliases.csv, hand-written after viewing the data): generic and near-synonym words -> a node at any level (family,
    category or term), or IGNORE for colour and mouthfeel words;
 3. any other word -> the node `5_other` (variant "other kept") or dropped (variant "other dropped").
A descriptor becomes the set of nodes of its words; an empty set is missing. "n\\a" answers are missing as in the main pipeline.

Three agreement measures on the same machinery as semantic_irr.py (pair similarity pooled over participant pairs and items; chance =
each participant's descriptors shuffled across items; kappa = (obs - exp) / (1 - exp); participant bootstrap CI):
 - embedding: Qwen3-Embedding-0.6B (aroma/flavor instruction) on the node terms joined by space;
 - node Jaccard: overlap of the node sets;
 - family Jaccard: overlap of the sets of level-1 wheel families.
Stimulation vs sham per measure with the paired comparison of compare_conditions.py. Coverage (descriptors kept) is reported.
Outputs (irr/outputs/): sca_mapping_summary.csv, sca_mapping_comparison.csv, sca_mapping_audit.csv, sca_mapping_report.md
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd

import semantic_irr as sir
from compare_conditions import compare, kappa_of

WHEEL = sir.ROOT / "data" / "SCA flavor wheel.csv"
ALIASES = sir.ROOT / "data" / "sca_aliases.csv"
OTHER = "5_other"


def strip_prefix(x: str) -> str:
    return re.sub(r"^\w+?_", "", x)


def build_vocab():
    """-> nodes {id: (family, term text)}, auto {cleaned word tuple: node id}, log of skipped wheel terms."""
    w = pd.read_csv(WHEEL)
    w["1st level"] = w["1st level"].ffill()
    w["2nd level"] = w["2nd level"].ffill()
    nodes, auto, skipped = {}, {}, []

    def add_auto(term: str, node: str, split: bool):
        parts = term.split("/") if split else [term]
        for part in parts:
            raw_n = len(re.findall(r"[a-z']+", sir.standardise_spelling(part)))
            cl = sir.clean_descriptor(part)
            if not cl or len(cl.split()) != raw_n:
                skipped.append((part, node))
                continue
            auto[tuple(cl.split())] = node

    for fam in w["1st level"].unique():
        nodes[fam] = (fam, strip_prefix(fam))
    for _, r in w.iterrows():
        fam, cat, leaf = r["1st level"], r["2nd level"], r["3rd level"]
        cid = f"{fam}|{cat}"
        if cid not in nodes:
            nodes[cid] = (fam, strip_prefix(cat))
            add_auto(strip_prefix(cat), cid, split=False)
    for _, r in w.iterrows():  # terms last so they win over category names
        if isinstance(r["3rd level"], str):
            lid = f"{r['1st level']}|{r['2nd level']}|{r['3rd level']}"
            nodes[lid] = (r["1st level"], sir.standardise_spelling(r["3rd level"]).replace("-", " "))
            add_auto(r["3rd level"], lid, split=True)
    nodes[OTHER] = (OTHER, "other")
    return nodes, auto, skipped


def load_aliases(nodes):
    a = pd.read_csv(ALIASES)
    amap = {}
    for r in a.itertuples(index=False):
        if r.node != "IGNORE" and r.node not in nodes:
            raise ValueError(f"alias {r.word!r}: unknown node {r.node!r}")
        amap[tuple(re.findall(r"[a-z']+", r.word.lower()))] = r.node  # written as they appear after cleaning
    return amap


def map_words(cleaned: str, auto, amap, keep_other: bool):
    """-> (set of nodes, list of (word or phrase, node/IGNORE/other, source))."""
    toks = cleaned.split()
    i, nodes, log = 0, set(), []
    while i < len(toks):
        for n in (3, 2, 1):
            key = tuple(toks[i:i + n])
            if len(key) < n:
                continue
            if key in amap:
                node, src = amap[key], "alias"
            elif key in auto:
                node, src = auto[key], "wheel"
            else:
                continue
            log.append((" ".join(key), node, src))
            if node != "IGNORE":
                nodes.add(node)
            i += n
            break
        else:
            log.append((toks[i], OTHER if keep_other else "dropped", "no wheel home"))
            if keep_other:
                nodes.add(OTHER)
            i += 1
    return nodes, log


def jaccard_matrix(sets: list[frozenset]) -> np.ndarray:
    n = len(sets)
    M = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            u = len(sets[i] | sets[j])
            M[i, j] = M[j, i] = len(sets[i] & sets[j]) / u if u else 1.0
    return M


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

    nodes, auto, skipped = build_vocab()
    amap = load_aliases(nodes)
    print(f"{len(nodes)} wheel nodes, {len(auto)} automatic wheel entries, {len(amap)} aliases; skipped wheel terms: {skipped}")

    df = sir.load(sir.DEFAULT_INPUT)
    items = sorted(df["item"].unique())
    model = SentenceTransformer(args.model)
    summ, comp, audit, cover = [], [], [], []

    for variant, keep_other in (("other kept (5_other)", True), ("other dropped", False)):
        sets_by_col, n_cleaned = {}, {}
        for col in sir.FIELDS:
            out = []
            ncl = 0
            for x in df[col]:
                cl = None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)
                if cl is None:
                    out.append(None)
                    continue
                ncl += 1
                ns, log = map_words(cl, auto, amap, keep_other)
                for word, node, src in log:
                    audit.append(dict(variant=variant, word=word, node=node, source=src))
                out.append(frozenset(ns) if ns else None)
            sets_by_col[col], n_cleaned[col] = out, ncl
        for col, fname in sir.FIELDS.items():
            kept = sum(s is not None for s in sets_by_col[col])
            cover.append(dict(variant=variant, field=fname, descriptors_cleaned=n_cleaned[col], descriptors_mapped=kept,
                              participants_with_any=int(df.loc[[s is not None for s in sets_by_col[col]], "subject"].nunique())))

        measures = {}
        for measure in ("embedding", "node Jaccard", "family Jaccard"):
            lab_of = {}
            for col in sir.FIELDS:
                if measure == "family Jaccard":
                    lab_of[col] = [None if s is None else frozenset(nodes[n][0] for n in s) for s in sets_by_col[col]]
                else:
                    lab_of[col] = sets_by_col[col]
            uniq = sorted({s for c in sir.FIELDS for s in lab_of[c] if s is not None}, key=lambda s: sorted(s))
            idx = {s: i for i, s in enumerate(uniq)}
            if measure == "embedding":
                texts = [" ".join(sorted({nodes[n][1] for n in s})) for s in uniq]
                E = np.asarray(model.encode([args.instruction + t for t in texts], batch_size=16, show_progress_bar=False), dtype=float)
                E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
                M = np.clip(np.einsum("id,jd->ij", E, E), -1, 1)
            else:
                M = jaccard_matrix(uniq)
            measures[measure] = (lab_of, idx, M)

        for measure, (lab_of, idx, M) in measures.items():
            for col, fname in sir.FIELDS.items():
                Ls = {}
                for cond in sir.CONDITIONS:
                    sub = df[df["condition"] == cond].copy()
                    sub["lbl"] = [lab_of[col][i] for i in sub.index]
                    Ls[cond], parts = sir.label_matrix(sub, idx, items)
                for cond in sir.CONDITIONS:
                    L = Ls[cond]
                    P = L.shape[0]
                    rng = np.random.default_rng(args.seed)
                    ids = np.arange(P)
                    obs = sir.pair_stats(L, M, ids)[0]
                    exp = sir.expected(L, M, ids, args.permutations, rng)
                    bk = np.empty(args.n_iter)
                    for b in range(args.n_iter):
                        bi = rng.integers(0, P, P)
                        bk[b] = kappa_of(L[bi], M, bi, args.boot_perms, rng)
                    lo, hi = np.nanpercentile(bk, [2.5, 97.5])
                    summ.append(dict(variant=variant, measure=measure, field=fname, condition=cond, n_descriptors=int((L >= 0).sum()),
                                     similarity_observed=obs, similarity_expected=exp, semantic_kappa=sir.kappa(obs, exp), ci_low=lo, ci_high=hi))
                r = compare(Ls["stimulation"], Ls["sham"], M, np.random.default_rng(args.seed), args.n_iter, args.permutations, args.boot_perms)
                comp.append(dict(variant=variant, measure=measure, field=fname, **r))
                print(f"{variant:21} {measure:14} {fname:12} stim {r['kappa_stimulation']:.3f} sham {r['kappa_sham']:.3f} "
                      f"delta {r['delta']:+.3f} [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] p = {r['p_perm']:.2f}")

    sdf, cdf, cov = pd.DataFrame(summ), pd.DataFrame(comp), pd.DataFrame(cover)
    adf = pd.DataFrame(audit).groupby(["variant", "word", "node", "source"]).size().rename("count").reset_index().sort_values(["variant", "count"], ascending=[True, False])
    sdf.to_csv(sir.OUT_DIR / "sca_mapping_summary.csv", index=False, float_format="%.6f")
    cdf.to_csv(sir.OUT_DIR / "sca_mapping_comparison.csv", index=False, float_format="%.6f")
    adf.to_csv(sir.OUT_DIR / "sca_mapping_audit.csv", index=False)

    md = ["# Agreement after mapping to the SCA flavor wheel (exploratory)", "",
          f"Model {args.model} with instruction {args.instruction.strip()!r} for the embedding measure; chance = {args.permutations} shuffles; "
          f"CI and p = participant bootstrap / condition swap with {args.n_iter} iterations; seed {args.seed}.", "",
          "## Coverage", "", "| Variant | Field | Descriptors after main cleaning | Mapped (non-empty) | Participants with any |", "|---|---|---:|---:|---:|"]
    md += [f"| {r.variant} | {r.field} | {r.descriptors_cleaned} | {r.descriptors_mapped} | {r.participants_with_any} |" for r in cov.itertuples()]
    md += ["", "## Kappa per condition", "", "| Variant | Measure | Field | Condition | Descriptors | Observed | Expected | Kappa [95% CI] |", "|---|---|---|---|---:|---:|---:|---|"]
    md += [f"| {r.variant} | {r.measure} | {r.field} | {r.condition} | {r.n_descriptors} | {r.similarity_observed:.3f} | {r.similarity_expected:.3f} | "
           f"{r.semantic_kappa:.3f} [{r.ci_low:.3f}, {r.ci_high:.3f}] |" for r in sdf.itertuples()]
    md += ["", "## Stimulation vs sham", "", "| Variant | Measure | Field | Stimulation | Sham | Delta [95% CI] | p |", "|---|---|---|---:|---:|---|---:|"]
    md += [f"| {r.variant} | {r.measure} | {r.field} | {r.kappa_stimulation:.3f} | {r.kappa_sham:.3f} | {r.delta:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}] | {r.p_perm:.2f} |"
           for r in cdf.itertuples()]
    (sir.OUT_DIR / "sca_mapping_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
