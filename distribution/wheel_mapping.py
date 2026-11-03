"""SCA flavor wheel mapping shared by the analyses: cleaned descriptor words -> wheel nodes.

Wheel terms (data/SCA flavor wheel.csv: level-3 terms and level-2 category names, cleaned with the main pipeline of irr/semantic_irr.py;
longest match first, up to 3 words) take part automatically, except a wheel term whose cleaning drops a word (e.g. "under ripe").
data/sca_aliases.csv (hand-written after viewing the data) maps generic and near-synonym words to a node at any level (or IGNORE for
colour and mouthfeel words); any other word goes to the node `5_other`. A node id is the path "family|category|term" with the wheel's own
names (e.g. `2_fruity|2a_berry|raspberry`); a family is `2_fruity`, a category `2_fruity|2a_berry`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "irr"))
import semantic_irr as sir  # noqa: E402

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
