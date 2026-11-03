#!/usr/bin/env python3
"""Can cosine similarity to wheel-category prototypes recover the wheel mapping? (validation only; no mapping is changed)

Every word or phrase unit that the current mapping (wheel_mapping.py: wheel terms + data/sca_aliases.csv) places on the wheel is classified
by the nearest level-2 category by cosine similarity (Qwen3-Embedding-0.6B, aroma/flavor instruction); the level-1 family is the parent of
the predicted category. Units mapped to the family only ("fruit", "spice") are checked at level 1 only. Truth = the current mapping.
Category representations compared:
 - prototype: normalised mean embedding of the category name and its level-3 terms;
 - label: embedding of the category name alone.
Wheel-term units are members of their own prototype, so they are classified leave-one-out (the unit is removed from its category's prototype;
units that are the only member, e.g. "tobacco", are skipped). Alias units are not members and need no correction: they are the fair test of
how well the rule catches words beyond the wheel's own vocabulary. Units without a wheel home (`5_other`) have no truth; their predicted
category and cosine are listed to see what a threshold would have to reject.
Outputs (distribution/outputs/): cosine_mapping_units.csv, cosine_mapping_validation.md
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import wheel_mapping as wm

sir = wm.sir
OUT_DIR = Path(__file__).resolve().parent / "outputs"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=sir.DEFAULT_MODEL)
    ap.add_argument("--instruction", default=sir.INSTRUCTION)
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer

    nodes, auto, _ = wm.build_vocab()
    amap = wm.load_aliases(nodes)
    cats = sorted(n for n in nodes if n.count("|") == 1)
    members = {c: [(nodes[c][1], True)] + [(nodes[n][1], False) for n in nodes if n.startswith(c + "|")] for c in cats}

    df = sir.load(sir.DEFAULT_INPUT)
    units = {}
    for col in sir.FIELDS:
        for x in df[col]:
            cl = None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)
            if cl is None:
                continue
            for u, node, src in wm.map_words(cl, auto, amap, True)[1]:
                if node != "IGNORE":
                    units[(u, node, src)] = units.get((u, node, src), 0) + 1

    model = SentenceTransformer(args.model)

    def emb(texts):
        E = np.asarray(model.encode([args.instruction + t for t in texts], batch_size=16, show_progress_bar=False), dtype=float)
        return E / np.maximum(np.linalg.norm(E, axis=1, keepdims=True), 1e-12)

    all_members = sorted({t for c in cats for t, _ in members[c]})
    Em = dict(zip(all_members, emb(all_members)))
    ul = [u for u, _, _ in units]
    Eu = dict(zip(sorted(set(ul)), emb(sorted(set(ul)))))
    Elab = {c: Em[nodes[c][1]] for c in cats}
    cleaned_key = {t: tuple((sir.clean_descriptor(t) or "").split()) for t in all_members}

    rows = []
    for (u, node, src), cnt in sorted(units.items(), key=lambda t: -t[1]):
        parts = node.split("|")
        truth_fam = parts[0]
        truth_cat = "|".join(parts[:2]) if len(parts) >= 2 and node != wm.OTHER else None
        ukey, e = tuple(u.split()), Eu[u]
        sims_proto, sims_label, skipped = {}, {}, False
        for c in cats:
            mem = [t for t, _ in members[c] if cleaned_key[t] != ukey]
            if len(mem) < len(members[c]) and not mem:
                skipped = skipped or (c == truth_cat)
                continue
            proto = np.sum([Em[t] for t in mem], axis=0)
            sims_proto[c] = float(np.einsum("d,d->", e, proto / np.linalg.norm(proto)))
            sims_label[c] = float(np.einsum("d,d->", e, Elab[c]))
        if skipped:
            continue
        r = dict(unit=u, node=node, source=src, count=cnt, truth_family=truth_fam, truth_category=truth_cat)
        for name, sims in (("proto", sims_proto), ("label", sims_label)):
            order = sorted(sims, key=sims.get, reverse=True)
            r[f"{name}_pred_category"], r[f"{name}_cos1"] = order[0], sims[order[0]]
            r[f"{name}_margin"] = sims[order[0]] - sims[order[1]]
            r[f"{name}_pred_family"] = order[0].split("|")[0]
        rows.append(r)
    res = pd.DataFrame(rows)
    OUT_DIR.mkdir(exist_ok=True)
    res.to_csv(OUT_DIR / "cosine_mapping_units.csv", index=False, float_format="%.4f")

    def acc(sub, name, level):
        s = sub[sub[f"truth_{level}"].notna()] if level == "category" else sub
        ok = s[f"{name}_pred_{level}"] == s[f"truth_{level}"]
        return len(s), ok.mean(), np.average(ok, weights=s["count"])

    md = ["# Cosine mapping validation (exploratory)", "",
          f"Model {args.model}; instruction {args.instruction.strip()!r}. Truth = current wheel + alias mapping. Units = words or phrases as matched "
          "(longest match first); token accuracy weights each unit by its occurrences in the data.", "",
          "## Accuracy", "", "| Units | Representation | Level | Units (n) | Type accuracy | Token accuracy |", "|---|---|---|---:|---:|---:|"]
    homed = res[res["node"] != wm.OTHER]
    for label, sub in (("wheel terms (leave-one-out)", homed[homed.source == "wheel"]), ("aliases", homed[homed.source == "alias"]), ("all mapped", homed)):
        for name in ("proto", "label"):
            for level in ("category", "family"):
                n, ta, wa = acc(sub, name, level)
                md.append(f"| {label} | {'prototype' if name == 'proto' else 'label only'} | {level} | {n} | {ta:.2f} | {wa:.2f} |")
    md += ["", "## Cosine of the best category (prototype)", "", "| Units | n | Median | 10th pct | 90th pct |", "|---|---:|---:|---:|---:|"]
    homed = homed.assign(correct=homed["proto_pred_category"] == homed["truth_category"])
    for label, sub in (("mapped, category correct", homed[homed.correct & homed.truth_category.notna()]),
                       ("mapped, category wrong", homed[~homed.correct & homed.truth_category.notna()]),
                       ("no wheel home (5_other)", res[res["node"] == wm.OTHER])):
        q = sub["proto_cos1"].quantile([0.5, 0.1, 0.9]).tolist() if len(sub) else [np.nan] * 3
        md.append(f"| {label} | {len(sub)} | {q[0]:.3f} | {q[1]:.3f} | {q[2]:.3f} |")
    md += ["", "## Threshold on the best cosine (prototype): mapped units kept and correct, no-home units rejected", "",
           "| Threshold | Mapped units kept | Of those, category correct | No-home units rejected (n = %d) |" % (res["node"] == wm.OTHER).sum(), "|---:|---:|---:|---:|"]
    cat_units = homed[homed.truth_category.notna()]
    oth = res[res["node"] == wm.OTHER]
    for t in np.round(np.arange(0.5, 0.86, 0.05), 2):
        kept = cat_units[cat_units.proto_cos1 >= t]
        md.append(f"| {t:.2f} | {len(kept)}/{len(cat_units)} | {(kept.proto_pred_category == kept.truth_category).mean() if len(kept) else float('nan'):.2f} | "
                  f"{(oth.proto_cos1 < t).sum()}/{len(oth)} |")
    md += ["", "## Units without a wheel home: what the rule would pick", "", "| Unit | Count | Best category | Cosine | Margin |", "|---|---:|---|---:|---:|"]
    md += [f"| {r.unit} | {r['count']} | {r.proto_pred_category} | {r.proto_cos1:.3f} | {r.proto_margin:.3f} |" for _, r in oth.sort_values("count", ascending=False).iterrows()]
    wrong = homed[~homed.correct & homed.truth_category.notna()].sort_values("count", ascending=False).head(15)
    md += ["", "## Most frequent mapped units the prototype rule gets wrong", "", "| Unit | Count | Truth | Predicted | Cosine |", "|---|---:|---|---|---:|"]
    md += [f"| {r.unit} | {r['count']} | {r.truth_category} | {r.proto_pred_category} | {r.proto_cos1:.3f} |" for _, r in wrong.iterrows()]
    (OUT_DIR / "cosine_mapping_validation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
