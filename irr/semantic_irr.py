#!/usr/bin/env python3
"""Between-participant semantic agreement within each tDCS condition, and stimulation vs sham.

Repurposed from altered-states-review/analyses/clustering/archive/sensitivity/inter_rater_reliability.py
(three fixed raters over clusters) for many participants who each describe the same coffee samples.

Design (data/tDCS.csv): each participant tastes 2 coffees (Brasil, Kenya) x 3 repeated tastings in each condition
(stimulation, sham) and writes two free-text descriptors per tasting (`notesaroma`, and the second text column, called
`flavor_notes` here; its header in the file is "bitter, roasted").
 - Cleaning per descriptor: spelling standardisation, spaCy lemmatisation, stop-word removal, lemma standardisation of synonym variants,
   removal of non-descriptor words (comparison, intensity, evaluation, mouthfeel; a descriptor left empty is missing); "n\\a" answers are
   missing. The raw -> cleaned map is written to cleaned_descriptors.csv. Embedding: Qwen3-Embedding-0.6B with the instruction
   "Embed aroma/flavor descriptors".
 - Space: MAIN = the embeddings centered on the occurrence-weighted mean descriptor embedding (removes the component shared by all
   coffee descriptors), rows normalised, compared by cosine. SENSITIVITY = the plain (uncentered) embeddings.
 - Rater = participant. Item = coffee x repeated tasting (6 items per condition). Analysed separately per condition and per text field.
 - Observed agreement = mean cosine similarity of two participants' descriptors, over all participant pairs that both answered an item,
   pooled over items. Chance = the same statistic after shuffling each participant's descriptors across the items of that condition
   (keeps each participant's own vocabulary, breaks the link to the item), mean over `--permutations` shuffles.
 - Semantic kappa = (observed - expected) / (1 - expected). 0 = chance, 1 = identical descriptors.
 - 95% CI: participant bootstrap (participants resampled with replacement; pairs of a participant with its own copy excluded; expected
   similarity recomputed in every bootstrap sample with `--boot-perms` shuffles).
 - Stimulation vs sham: delta = kappa(stimulation) - kappa(sham) per field. Every participant contributes to both conditions, so the CI is a
   paired participant bootstrap and p comes from swapping each participant's stimulation and sham descriptor sets with probability 1/2
   (n = --n-iter); BH-FDR q over the 2 fields, within each space.
Everything is exploratory; the cleaning rules were written after viewing the data.

Outputs (irr/outputs/): irr_summary.csv, irr_comparison.csv, irr_report.md, cleaned_descriptors.csv
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

DEFAULT_MODEL = "Qwen/Qwen3-Embedding-0.6B"
INSTRUCTION = "Instruct: Embed aroma/flavor descriptors.\nText: "
FIELDS = {"notesaroma": "notesaroma", "bitter, roasted": "flavor_notes"}
CONDITIONS = ["stimulation", "sham"]

# Spelling standardisation: misspellings and spelling variants. Listed after viewing every word in both text columns (exploratory).
TYPO_FIXES = {
    "acisic": "acidic", "asky": "ashy", "carmel": "caramel", "carmelised": "caramelized", "carmelized": "caramelized",
    "ceral": "cereal", "chamomille": "chamomile", "dack": "dark", "dilater": "diluted", "dreid": "dried", "druity": "fruity",
    "lemoc": "lemon", "majoram": "marjoram", "moky": "smoky", "pepermint": "peppermint", "pomegranade": "pomegranate",
    "pomegrannate": "pomegranate", "pomergranate": "pomegranate", "pommergranate": "pomegranate", "rasberry": "raspberry",
    "rosdy": "roasty", "slighlty": "slightly", "blackcurrent": "blackcurrant", "rost": "roast", "smokey": "smoky",
    "flavour": "flavor", "flavours": "flavors", "caramelised": "caramelized", "anis": "anise", "choco": "chocolate", "coca": "cocoa", "veggie": "vegetable", "veggies": "vegetable",
}
# Lemma standardisation: lemmas of the same descriptor written differently (applied after lemmatisation).
LEMMA_CANON = {
    "burned": "burnt", "burn": "burnt", "chocolaty": "chocolate", "chocolatey": "chocolate", "roasty": "roast", "roasted": "roast",
    "smoked": "smoky", "fruity": "fruit", "berrylike": "berry", "caramelized": "caramel", "caramelize": "caramel", "dilute": "watery", "smoke": "smoky", "water": "watery", "sugary": "sugar", "nutty": "nut",
    "buttery": "butter", "creamy": "cream", "milky": "milk", "oily": "oil", "grainy": "grain", "earthy": "earth", "woody": "wood",
    "spicy": "spice", "sweetish": "sweet", "honeyed": "honey", "vegetative": "vegetable", "winey": "wine", "acid": "acidic",
    "sour": "sourness", "sweeter": "sweet", "watered": "watery", "diluted": "watery", "thin": "watery", "weaker": "weak",
}
# Words that are not aroma or flavor descriptors: comparison, intensity and degree, evaluation, mouthfeel and body, discourse words.
# Used by the main pipeline (clean_descriptor(..., descriptors_only=True)); the sensitivity runs also report it switched off; written after viewing the vocabulary.
NON_DESCRIPTORS = {
    "more", "less", "not", "no", "very", "much", "slightly", "slight", "strong", "weak", "mild", "intense", "light", "full", "heavy",
    "faint", "long", "short", "thin", "thinner", "thick", "soft", "smooth", "flat", "bland", "neutral", "better", "worse", "worst", "bad",
    "good", "same", "before", "half", "combination", "consistent", "watery", "liquidy", "wet", "hard", "warm", "nor", "never", "most",
    "least", "few", "enough", "fully", "gets",
}
# Tokens the lemmatizer reads as the wrong word class ("rose" the flower as the verb "rise").
KEEP_TOKEN = {"rose": "rose", "better": "better"}
# Stop words: scikit-learn English list without negation and degree words (which change a descriptor's meaning), plus filler
# words of tasting notes that carry no aroma or flavor information.
KEEP = {"not", "no", "nor", "never", "less", "more", "very", "much", "most", "least", "few", "full", "fully", "enough"}
FILLER = {"aroma", "aromatics", "flavor", "flavors", "taste", "smell", "note", "notes", "coffee", "aftertaste", "mouth", "hint", "bit",
          "little", "time", "maybe", "perhaps", "definitely", "still", "like", "kind", "sort", "something", "undertone", "accurate", "n", "bis"}
STOP_WORDS = (set(ENGLISH_STOP_WORDS) - KEEP) | FILLER


def standardise_spelling(text: str) -> str:
    """Lowercase, collapse whitespace, fix misspellings and spelling variants (word by word)."""
    s = re.sub(r"\s+", " ", str(text).strip().lower())
    return re.sub(r"[a-z']+", lambda m: TYPO_FIXES.get(m.group(0), m.group(0)), s)


NA_RE = re.compile(r"^n[\\/]a$")
_NLP = None


def lemmatise(text: str) -> list[str]:
    """spaCy lemmas of the alphabetic tokens (en_core_web_sm; tagger and lemmatizer only)."""
    global _NLP
    if _NLP is None:
        import spacy

        _NLP = spacy.load("en_core_web_sm", disable=["parser", "ner"])
    return [(t.lemma_.lower(), t.text) for t in _NLP(text) if t.is_alpha]


def clean_descriptor(text: str, spelling: bool = True, lemma: bool = True, stop: bool = True, canon: bool = True,
                     descriptors_only: bool = True) -> str | None:
    """spelling standardisation -> lemmatisation -> stop-word removal -> lemma standardisation (synonym variants) -> unique tokens.
    Each step can be switched off (all on in the analyses); with all four off the text is only lowercased and whitespace-collapsed.
    "n\\a" (not available) is a non-response and returns None (missing). descriptors_only (main pipeline) drops NON_DESCRIPTORS words and returns None
    when nothing is left; without it a descriptor with no words left falls back to its raw text."""
    if NA_RE.match(str(text).strip().lower()):
        return None
    base = standardise_spelling(text) if spelling else re.sub(r"\s+", " ", str(text).strip().lower())
    if not (lemma or stop or canon):
        return base
    pairs = lemmatise(base) if lemma else [(t, t) for t in re.findall(r"[a-z']+", base)]
    out = []
    for lem, tok in pairs:
        if stop and (tok in STOP_WORDS or lem in STOP_WORDS):
            continue
        if lemma:
            lem = KEEP_TOKEN.get(tok, lem)
        if canon:
            lem = LEMMA_CANON.get(lem, lem)
        if descriptors_only and lem in NON_DESCRIPTORS:
            continue
        if lem not in out:
            out.append(lem)
    if descriptors_only:
        return " ".join(out) if out else None
    return " ".join(out) if out else base


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


def bh_fdr(p) -> np.ndarray:
    """Benjamini-Hochberg adjusted p-values (q-values)."""
    p = np.asarray(p, dtype=float)
    n = len(p)
    order = np.argsort(p)
    q = np.empty(n)
    run = 1.0
    for rank in range(n - 1, -1, -1):
        run = min(run, p[order[rank]] * n / (rank + 1))
        q[order[rank]] = run
    return q


def kappa(obs: float, exp: float) -> float:
    return (obs - exp) / (1.0 - exp) if abs(1.0 - exp) > 1e-12 else np.nan



def kappa_of(L, M, ids, n_perm, rng):
    return kappa(pair_stats(L, M, ids)[0], expected(L, M, ids, n_perm, rng))


def compare(A, B, M, rng, n_iter, perms, boot_perms):
    """Paired comparison of kappa(A) - kappa(B): participant bootstrap CI and condition-swap permutation p."""
    P = A.shape[0]
    ids = np.arange(P)
    ka, kb = kappa_of(A, M, ids, perms, rng), kappa_of(B, M, ids, perms, rng)
    d_obs = ka - kb
    boot = np.empty(n_iter)
    for b in range(n_iter):
        idx = rng.integers(0, P, P)
        boot[b] = kappa_of(A[idx], M, idx, boot_perms, rng) - kappa_of(B[idx], M, idx, boot_perms, rng)
    null = np.empty(n_iter)
    for b in range(n_iter):
        sw = rng.random(P) < 0.5
        A2, B2 = np.where(sw[:, None], B, A), np.where(sw[:, None], A, B)
        null[b] = kappa_of(A2, M, ids, boot_perms, rng) - kappa_of(B2, M, ids, boot_perms, rng)
    p = (1 + (np.abs(null) >= abs(d_obs) - 1e-12).sum()) / (1 + n_iter)
    lo, hi = np.nanpercentile(boot, [2.5, 97.5])
    return dict(kappa_stimulation=ka, kappa_sham=kb, delta=d_obs, ci_low=lo, ci_high=hi, p_perm=p)


def unit_rows(X):
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--instruction", default=INSTRUCTION)
    ap.add_argument("--permutations", type=int, default=2000)
    ap.add_argument("--n-iter", type=int, default=1000, help="bootstrap and swap iterations")
    ap.add_argument("--boot-perms", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    df = load(args.input)
    items = sorted(df["item"].unique())
    lab = {c: df[c].map(lambda x: None if pd.isna(x) or not str(x).strip() else clean_descriptor(x)) for c in FIELDS}
    uniq = sorted({v for c in FIELDS for v in lab[c].dropna()})
    idx = {v: i for i, v in enumerate(uniq)}
    OUT_DIR.mkdir(exist_ok=True)
    pd.concat([df[[c]].assign(cleaned=lab[c], field=f).rename(columns={c: "raw"}) for c, f in FIELDS.items()]).dropna().drop_duplicates() \
        .sort_values(["field", "raw"]).to_csv(OUT_DIR / "cleaned_descriptors.csv", index=False)
    print(f"{df.subject.nunique()} participants, {len(items)} items per condition, {len(uniq)} unique cleaned descriptors")

    E = unit_rows(np.asarray(SentenceTransformer(args.model).encode([args.instruction + u for u in uniq], batch_size=16, show_progress_bar=False), dtype=float))
    occ = np.array([sum((lab[c] == u).sum() for c in FIELDS) for u in uniq], dtype=float)
    Ec = unit_rows(E - np.average(E, axis=0, weights=occ))
    spaces = {"centered (main)": np.clip(np.einsum("ud,vd->uv", Ec, Ec), -1, 1), "plain (sensitivity)": np.clip(np.einsum("ud,vd->uv", E, E), -1, 1)}

    summ, comp = [], []
    for space, M in spaces.items():
        for col, fname in FIELDS.items():
            Ls = {}
            for cond in CONDITIONS:
                sub = df[df["condition"] == cond].copy()
                sub["lbl"] = lab[col][sub.index]
                Ls[cond], _ = label_matrix(sub, idx, items)
            for cond in CONDITIONS:
                L = Ls[cond]
                P = L.shape[0]
                rng = np.random.default_rng(args.seed)
                ids = np.arange(P)
                obs = pair_stats(L, M, ids)[0]
                exp = expected(L, M, ids, args.permutations, rng)
                bk = np.empty(args.n_iter)
                for b in range(args.n_iter):
                    bi = rng.integers(0, P, P)
                    bk[b] = kappa_of(L[bi], M, bi, args.boot_perms, rng)
                lo, hi = np.nanpercentile(bk, [2.5, 97.5])
                summ.append(dict(space=space, field=fname, condition=cond, n_participants=P, n_descriptors=int((L >= 0).sum()), similarity_observed=obs,
                                 similarity_expected=exp, semantic_kappa=kappa(obs, exp), ci_low=lo, ci_high=hi))
            r = compare(Ls["stimulation"], Ls["sham"], M, np.random.default_rng(args.seed), args.n_iter, args.permutations, args.boot_perms)
            comp.append(dict(space=space, field=fname, **r))
            print(f"{space:20} {fname:12} stim {r['kappa_stimulation']:.3f} sham {r['kappa_sham']:.3f} delta {r['delta']:+.3f} "
                  f"[{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] p = {r['p_perm']:.2f}")
    sdf, cdf = pd.DataFrame(summ), pd.DataFrame(comp)
    cdf["q_bh"] = np.concatenate([bh_fdr(g["p_perm"]) for _, g in cdf.groupby("space", sort=False)])
    sdf.to_csv(OUT_DIR / "irr_summary.csv", index=False, float_format="%.6f")
    cdf.to_csv(OUT_DIR / "irr_comparison.csv", index=False, float_format="%.6f")

    md = ["# Between-participant semantic agreement, stimulation vs sham (exploratory)", "",
          f"{df.subject.nunique()} participants; items = coffee x repeated tasting ({len(items)} per condition); {len(uniq)} unique cleaned descriptors; model {args.model}, "
          f"instruction {args.instruction.strip()!r}. Main space = embeddings centered on the descriptor mean; sensitivity = plain embeddings. Chance = {args.permutations} shuffles; "
          f"CI and p = participant bootstrap / condition swap with {args.n_iter} iterations; seed {args.seed}.", "",
          "## Kappa per condition", "", "| Space | Field | Condition | Participants | Descriptors | Observed | Expected | Kappa [95% CI] |", "|---|---|---|---:|---:|---:|---:|---|"]
    md += [f"| {r.space} | {r.field} | {r.condition} | {r.n_participants} | {r.n_descriptors} | {r.similarity_observed:.3f} | {r.similarity_expected:.3f} | "
           f"{r.semantic_kappa:.3f} [{r.ci_low:.3f}, {r.ci_high:.3f}] |" for r in sdf.itertuples()]
    md += ["", "## Stimulation vs sham", "", "| Space | Field | Stimulation | Sham | Delta [95% CI] | p | q (BH, 2 fields) |", "|---|---|---:|---:|---|---:|---:|"]
    md += [f"| {r.space} | {r.field} | {r.kappa_stimulation:.3f} | {r.kappa_sham:.3f} | {r.delta:+.3f} [{r.ci_low:+.3f}, {r.ci_high:+.3f}] | {r.p_perm:.2f} | {r.q_bh:.2f} |"
           for r in cdf.itertuples()]
    (OUT_DIR / "irr_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
