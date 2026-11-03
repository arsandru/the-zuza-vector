#!/usr/bin/env python3
"""Can cosine similarity to wheel prototypes recover the wheel + alias mapping? (validation only; no mapping is changed)

Units = words or phrases as matched by wheel_mapping.map_words (longest match first). Truth = the current mapping: wheel terms and the
alias file. Units the alias file sends to `5_other` or IGNORE are manual decisions and are not classified. Each remaining unit is assigned
to the category with the highest cosine (Qwen3-Embedding-0.6B, aroma/flavor instruction) to the category prototype, the mean embedding of
 - "L2+L3": the category name and its terms;
 - "L1+L2+L3": the family name, the category name and its terms.
The family is read either as the parent of the predicted category ("parent") or from the family's own prototype (family name, category
names and terms; "own"). Units mapped to a family only ("fruit", "spice") are scored at the family level only.
Wheel-term units are members of their own prototype and are classified leave-one-out (the unit's text is removed from every prototype;
a unit that is the only member of its category, e.g. "tobacco", is skipped). Alias units need no correction: they test how well the rule
catches words beyond the wheel's own vocabulary.
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

    nodes, auto, _ = wm.build_vocab()
    amap = wm.load_aliases(nodes)
    units = {}
    for col in sir.FIELDS:
        for x in sir.load(sir.DEFAULT_INPUT)[col]:
            cl = None if pd.isna(x) or not str(x).strip() else sir.clean_descriptor(x)
            if cl is None:
                continue
            for u, node, src in wm.map_words(cl, auto, amap, True)[1]:
                if node not in ("IGNORE", wm.OTHER):
                    units[(u, node, src)] = units.get((u, node, src), 0) + 1

    embed = wm.make_embedder(args.model, args.instruction)
    modes = {m: wm.member_texts(nodes, m) for m in ("l23", "l123")}
    texts = sorted({t for cats, fams, ct, ft in modes.values() for d in (ct, ft) for ts in d.values() for t in ts} | {u for u, _, _ in units})
    Em = dict(zip(texts, embed(texts)))
    ckey = {t: tuple((sir.clean_descriptor(t) or "").split()) for t in texts}

    rows = []
    for (u, node, src), cnt in sorted(units.items(), key=lambda t: -t[1]):
        parts = node.split("|")
        truth_cat = "|".join(parts[:2]) if len(parts) >= 2 else None
        e = Em[u]
        drop = {t for t in texts if ckey[t] == tuple(u.split())} if src == "wheel" else set()
        r = dict(unit=u, node=node, source=src, count=cnt, truth_family=parts[0], truth_category=truth_cat)
        skip = False
        for mode, (cats, fams, ctext, ftext) in modes.items():
            cid, Pc = wm.prototypes(ctext, Em, drop)
            fid, Pf = wm.prototypes(ftext, Em, drop)
            if truth_cat and truth_cat not in cid:
                skip = True
                break
            sc = np.einsum("d,kd->k", e, Pc)
            sf = np.einsum("d,kd->k", e, Pf)
            o = np.argsort(-sc)
            r[f"{mode}_cat"], r[f"{mode}_cos"], r[f"{mode}_margin"] = cid[o[0]], sc[o[0]], sc[o[0]] - sc[o[1]]
            r[f"{mode}_fam_parent"] = cid[o[0]].split("|")[0]
            r[f"{mode}_fam_own"] = fid[int(np.argmax(sf))]
        if not skip:
            rows.append(r)
    res = pd.DataFrame(rows)
    OUT_DIR.mkdir(exist_ok=True)
    res.to_csv(OUT_DIR / "cosine_mapping_units.csv", index=False, float_format="%.4f")

    def acc(sub, col, truth):
        s = sub[sub[truth].notna()]
        ok = (s[col] == s[truth]).to_numpy()
        return len(s), ok.mean(), np.average(ok, weights=s["count"])

    md = ["# Cosine mapping validation (exploratory)", "",
          f"Model {args.model}; instruction {args.instruction.strip()!r}. Truth = current wheel + alias mapping (units sent to `5_other` or IGNORE by the "
          "alias file are manual decisions and not classified). Token accuracy weights each unit by its occurrences in the data.", "",
          "## Accuracy", "", "| Units | Prototype | Level | Units (n) | Type accuracy | Token accuracy |", "|---|---|---|---:|---:|---:|"]
    for label, sub in (("wheel terms (leave-one-out)", res[res.source == "wheel"]), ("aliases", res[res.source == "alias"]), ("all", res)):
        for mode, mname in (("l23", "L2+L3"), ("l123", "L1+L2+L3")):
            for col, truth, lvl in ((f"{mode}_cat", "truth_category", "category"), (f"{mode}_fam_parent", "truth_family", "family (parent of category)"),
                                    (f"{mode}_fam_own", "truth_family", "family (own prototype)")):
                n, ta, wa = acc(sub, col, truth)
                md.append(f"| {label} | {mname} | {lvl} | {n} | {ta:.2f} | {wa:.2f} |")
    wrong = res[(res.l123_cat != res.truth_category) & res.truth_category.notna()].sort_values("count", ascending=False).head(15)
    md += ["", "## Most frequent units the L1+L2+L3 prototype rule assigns to a different category than the current mapping", "",
           "| Unit | Count | Current mapping | Cosine mapping | Cosine |", "|---|---:|---|---|---:|"]
    md += [f"| {r.unit} | {r['count']} | {r.truth_category} | {r.l123_cat} | {r.l123_cos:.3f} |" for _, r in wrong.iterrows()]
    (OUT_DIR / "cosine_mapping_validation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
