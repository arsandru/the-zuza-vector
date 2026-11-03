#!/usr/bin/env python3
"""Between-participant semantic agreement within each tDCS condition.

Repurposed from altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py
(three fixed raters over clusters) for many participants who each describe the same coffee samples.

Design (data/tDCS.csv): each participant tastes 2 coffees (Brasil, Kenya) x 3 repeated tastings in each condition
(stimulation, sham) and writes two free-text descriptors per tasting (`notesaroma`, and the second text column, called
`flavor_notes` here; its header in the file is "bitter, roasted").
 - Rater = participant. Item = coffee x repeated tasting (6 items per condition). Analysed separately per condition and per text field.
 - Observed agreement = mean cosine similarity of the embeddings of two participants' cleaned descriptors, over all participant pairs
   that both answered an item, pooled over items.
 - Chance = same statistic after shuffling each participant's descriptors across the items of that condition (keeps each participant's
   own vocabulary, breaks the link to the item). Mean over `--permutations` shuffles.
 - Semantic kappa = (observed - expected) / (1 - expected). 0 = chance, 1 = identical descriptors.
 - 95% CI: participant bootstrap (participants resampled with replacement; pairs of a participant with its own copy excluded;
   expected similarity recomputed in every bootstrap sample with `--boot-perms` shuffles).
 - Sensitivity: second embedding model; thresholded agreement (pair similarity >= t) with the same chance correction.
Everything here is descriptive; the tDCS contrast between conditions is not tested.

Outputs (irr/outputs/): semantic_irr_summary.csv, semantic_irr_per_item.csv, semantic_irr_report.md
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "tDCS.csv"
OUT_DIR = Path(__file__).resolve().parent / "outputs"

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
SECOND_MODEL = "sentence-transformers/all-mpnet-base-v2"
FIELDS = {"notesaroma": "notesaroma", "bitter, roasted": "flavor_notes"}
CONDITIONS = ["stimulation", "sham"]

# Obvious misspellings found by listing every word in both text columns; written after looking at the data (exploratory cleaning).
TYPO_FIXES = {
    "acisic": "acidic", "asky": "ashy", "carmel": "caramel", "carmelised": "caramelized", "carmelized": "caramelized",
    "ceral": "cereal", "chamomille": "chamomile", "dack": "dark", "dilater": "diluted", "dreid": "dried", "druity": "fruity",
    "lemoc": "lemon", "majoram": "marjoram", "moky": "smoky", "pepermint": "peppermint", "pomegranade": "pomegranate",
    "pomegrannate": "pomegranate", "pomergranate": "pomegranate", "pommergranate": "pomegranate", "rasberry": "raspberry",
    "rosdy": "roasty", "slighlty": "slightly", "blackcurrent": "blackcurrant",
}


def normalize_label(x: str) -> str:
    s = re.sub(r"\s+", " ", str(x).strip().lower())
    return re.sub(r"[a-z']+", lambda m: TYPO_FIXES.get(m.group(0), m.group(0)), s)


def simple_lemma(t: str) -> str:
    if len(t) > 4 and t.endswith("ies"):
        return t[:-3] + "y"
    if len(t) > 4 and t.endswith("ing"):
        return t[:-3]
    if len(t) > 3 and t.endswith("ed"):
        return t[:-2]
    if len(t) > 3 and t.endswith("es"):
        return t[:-2]
    if len(t) > 2 and t.endswith("s"):
        return t[:-1]
    return t


def clean_for_distance(label: str) -> str:
    out = [simple_lemma(t) for t in re.findall(r"[a-z']+", label) if t not in ENGLISH_STOP_WORDS]
    return " ".join(out) if out else label


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
    df["condition"] = df["condition"].str.strip().str.lower()
    df["item"] = df["coffee"].astype(str) + " #" + df["repeated_ratings"].astype(str)
    return df


def label_matrix(sub: pd.DataFrame, emb_index: dict[str, int], items: list[str]) -> tuple[np.ndarray, list[str]]:
    """participants x items matrix of label indices, -1 = no descriptor."""
    parts = sorted(sub["subject"].unique())
    L = -np.ones((len(parts), len(items)), dtype=int)
    for r in sub.itertuples(index=False):
        v = r.lbl
        if v is not None:
            L[parts.index(r.subject), items.index(r.item)] = emb_index[v]
    return L, parts


def pair_stats(L: np.ndarray, M: np.ndarray, ids: np.ndarray, thr: float | None = None) -> tuple[float, int, np.ndarray]:
    """Pooled mean pair similarity (or share >= thr) over items; also per-item means. ids = original participant of each row."""
    S = M[L.T[:, :, None], L.T[:, None, :]]  # items x P x P
    if thr is not None:
        S = (S >= thr).astype(float)
    ok = (L.T[:, :, None] >= 0) & (L.T[:, None, :] >= 0) & (ids[None, :, None] != ids[None, None, :])
    n = ok.sum(axis=(1, 2))
    per_item = np.where(n > 0, (S * ok).sum(axis=(1, 2)) / np.maximum(n, 1), np.nan)
    return float((S * ok).sum() / ok.sum()), int(ok.sum() // 2), per_item


def expected(L, M, ids, n_perm, rng, thr=None) -> float:
    vals = np.empty(n_perm)
    for b in range(n_perm):
        order = np.argsort(rng.random(L.shape), axis=1)
        vals[b] = pair_stats(np.take_along_axis(L, order, axis=1), M, ids, thr)[0]
    return float(vals.mean())


def kappa(obs: float, exp: float) -> float:
    return (obs - exp) / (1.0 - exp) if abs(1.0 - exp) > 1e-12 else np.nan


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--second-model", default=SECOND_MODEL)
    ap.add_argument("--permutations", type=int, default=2000)
    ap.add_argument("--bootstraps", type=int, default=1000)
    ap.add_argument("--boot-perms", type=int, default=100)
    ap.add_argument("--thresholds", default="0.6,0.7,0.8")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    df = load(args.input)
    items = sorted(df["item"].unique())
    thresholds = [float(t) for t in args.thresholds.split(",")]
    models = [args.model] + ([args.second_model] if args.second_model and args.second_model != args.model else [])
    OUT_DIR.mkdir(exist_ok=True)

    for col in FIELDS:
        df[col + "_lbl"] = df[col].map(lambda x: None if pd.isna(x) or not str(x).strip() else clean_for_distance(normalize_label(x)))
    uniq = sorted({v for col in FIELDS for v in df[col + "_lbl"].dropna()})
    emb_index = {v: i for i, v in enumerate(uniq)}
    print(f"{df.subject.nunique()} participants, {len(items)} items per condition, {len(uniq)} unique cleaned descriptors")

    summ, per_item_rows = [], []
    for mname in models:
        E = np.asarray(SentenceTransformer(mname).encode(uniq, show_progress_bar=False), dtype=float)
        E /= np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)
        M = np.clip(np.einsum("id,jd->ij", E, E), -1, 1)  # einsum: spurious overflow warnings with E @ E.T on this machine
        for col, fname in FIELDS.items():
            for cond in CONDITIONS:
                sub = df[df["condition"] == cond].copy()
                sub["lbl"] = sub[col + "_lbl"]
                L, parts = label_matrix(sub, emb_index, items)
                P = len(parts)
                ids = np.arange(P)
                rng = np.random.default_rng(args.seed)
                obs, n_pairs, per_item = pair_stats(L, M, ids)
                exp = expected(L, M, ids, args.permutations, rng)
                k = kappa(obs, exp)
                bk = np.empty(args.bootstraps)
                for b in range(args.bootstraps):
                    idx = rng.integers(0, P, P)
                    Lb = L[idx]
                    ob = pair_stats(Lb, M, idx)[0]
                    bk[b] = kappa(ob, expected(Lb, M, idx, args.boot_perms, rng))
                lo, hi = np.nanpercentile(bk, [2.5, 97.5])
                row = dict(model=mname, field=fname, condition=cond, n_participants=P, n_descriptors=int((L >= 0).sum()),
                           n_pairs=n_pairs, similarity_observed=obs, similarity_expected=exp, semantic_kappa=k,
                           kappa_ci_low=lo, kappa_ci_high=hi)
                for t in thresholds:
                    o_t = pair_stats(L, M, ids, t)[0]
                    e_t = expected(L, M, ids, args.permutations // 4, rng, t)
                    row[f"kappa_thr_{t:.2f}"] = kappa(o_t, e_t)
                summ.append(row)
                for it, v in zip(items, per_item):
                    per_item_rows.append(dict(model=mname, field=fname, condition=cond, item=it,
                                              n_raters=int((L[:, items.index(it)] >= 0).sum()),
                                              mean_pair_similarity=v, kappa_vs_global_chance=kappa(v, exp)))
                print(f"{mname.split('/')[-1]:>20} {fname:12} {cond:12} kappa {k:.3f} [{lo:.3f}, {hi:.3f}]")

    sdf, pdf_ = pd.DataFrame(summ), pd.DataFrame(per_item_rows)
    sdf.to_csv(OUT_DIR / "semantic_irr_summary.csv", index=False, float_format="%.6f")
    pdf_.to_csv(OUT_DIR / "semantic_irr_per_item.csv", index=False, float_format="%.6f")

    tcols = [c for c in sdf.columns if c.startswith("kappa_thr_")]
    L_ = ["# Between-participant semantic agreement within condition (descriptive)", "",
          f"- Input: `{args.input.name}`; {df.subject.nunique()} participants; items = coffee x repeated tasting ({len(items)} per condition).",
          "- Rater = participant; each condition and text field analysed separately. Chance = each participant's descriptors shuffled across items "
          f"(n = {args.permutations}); CI = participant bootstrap (n = {args.bootstraps}, expected similarity recomputed with {args.boot_perms} shuffles).",
          f"- Cleaning: lowercase, {len(TYPO_FIXES)} misspelling fixes (written after viewing the data), stop-word removal, crude lemmatisation. Seed {args.seed}.",
          "- Not tested: the stimulation vs sham difference.", "",
          "| Model | Field | Condition | Participants | Descriptors | Pairs | Observed | Expected | Semantic kappa | 95% CI | " + " | ".join(f"kappa t={c[-4:]}" for c in tcols) + " |",
          "|---|---|---|---:|---:|---:|---:|---:|---:|---:|" + "---:|" * len(tcols)]
    for _, r in sdf.iterrows():
        L_.append(f"| {r.model.split('/')[-1]} | {r.field} | {r.condition} | {int(r.n_participants)} | {int(r.n_descriptors)} | {int(r.n_pairs)} | {r.similarity_observed:.3f} | "
                  f"{r.similarity_expected:.3f} | {r.semantic_kappa:.3f} | [{r.kappa_ci_low:.3f}, {r.kappa_ci_high:.3f}] | "
                  + " | ".join(f"{r[c]:.3f}" for c in tcols) + " |")
    (OUT_DIR / "semantic_irr_report.md").write_text("\n".join(L_) + "\n", encoding="utf-8")
    print(f"Saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
