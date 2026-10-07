"""Consolidate step-8 findings into one column-level decision list.

Reads the step-8 outputs (univariate flags, IV ranking, collinearity groups) and
emits a single CSV giving every feature column a decision:

    DROP (near-constant)   >=99% of rows are a single value
    DROP (collinear)       redundant with a higher-IV representative (|r| > 0.9)
    KEEP                   retained, with any transform noted
    ADD                    a derived feature to build

The decision rules are the ones documented in docs/eda_findings.md (step 8);
this script is only a faithful re-assembly of those results, so nothing here
changes the conclusions.

Run: python scripts/make_column_decisions.py
Output: results/eda/column_decisions.csv
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EDA = ROOT / "results" / "eda"


def main():
    iv = pd.read_csv(EDA / "iv_ranking.csv")
    flags = json.loads((EDA / "univariate_flags.json").read_text(encoding="utf-8"))
    groups = json.loads((EDA / "collinearity_groups.json").read_text(encoding="utf-8"))

    # true object columns (the 16 categoricals needing label/one-hot encoding)
    raw_head = pd.read_csv(ROOT / "data/raw/application_train.csv", nrows=5,
                           low_memory=False)
    object_cols = {c for c in raw_head.columns
                   if c not in ("SK_ID_CURR", "TARGET")
                   and str(raw_head[c].dtype) == "object"}

    near_constant = set(flags["near_constant"])
    log_transform = set(flags["log_transform"])
    high_card = set(flags["high_cardinality"])
    sparse_cont = set(flags["sparse_continuous"])
    sparse_cat = set(flags["sparse_categorical"])
    extreme = set(flags["extreme_outlier"])

    # collinear: map dropped column -> its representative
    collinear_drop = {}
    collinear_rep = set()
    for g in groups["groups"]:
        collinear_rep.add(g["representative"])
        for c in g["drop"]:
            collinear_drop[c] = g["representative"]

    rows = []
    for _, r in iv.iterrows():
        c = r["feature"]
        if c in near_constant:
            decision = "DROP"
            reason = "near-constant (>=99% single value)"
            transform = ""
        elif c in collinear_drop:
            decision = "DROP"
            reason = f"collinear with {collinear_drop[c]} (|r| > 0.9)"
            if c == "AMT_CREDIT":
                reason += "; its amount signal is absorbed by ANNUITY_TO_CREDIT"
            transform = ""
        else:
            decision = "KEEP"
            reason = ""
            transform = _transform(c, log_transform, high_card, sparse_cont,
                                   sparse_cat, extreme, object_cols)
        rows.append({
            "feature": c,
            "decision": decision,
            "transform": transform,
            "reason": reason,
            "iv": r["iv"],
            "type": r["type"],
        })

    # derived feature to add (the only ratio that beats both parents)
    rows.append({
        "feature": "ANNUITY_TO_CREDIT",
        "decision": "ADD",
        "transform": "AMT_ANNUITY / AMT_CREDIT; zero denominator -> NaN",
        "reason": "only derived ratio beating both parents (IV 0.0915 vs 0.0247/0.0448)",
        "iv": 0.0915,
        "type": "derived",
    })

    out = pd.DataFrame(rows)
    out = out.sort_values(["decision", "iv"], ascending=[True, False])
    out.to_csv(EDA / "column_decisions.csv", index=False)

    counts = out.decision.value_counts()
    n_drop = counts.get("DROP", 0)
    n_keep = counts.get("KEEP", 0)
    n_add = counts.get("ADD", 0)
    print(f"features: {len(iv)}  ->  KEEP {n_keep}, DROP {n_drop}, ADD {n_add}")
    print(f"  near-constant dropped: {len(near_constant)}")
    print(f"  collinear dropped:     {len(collinear_drop)}")
    print(f"  collinear reps kept:   {len(collinear_rep)}")
    print(f"  final model width:     {n_keep + n_add} (train fold, before encoding)")
    print("\n=== DROP (near-constant) ===")
    print(out.loc[out.decision == "DROP", "feature"].tolist()[:0] or
          sorted(near_constant))
    print("\n=== KEEP with transform (first 25) ===")
    keep_t = out[(out.decision == "KEEP") & (out.transform != "")]
    print(keep_t[["feature", "transform"]].head(25).to_string(index=False))
    print("\n=== full list saved to results/eda/column_decisions.csv ===")


def _transform(c, log_transform, high_card, sparse_cont, sparse_cat, extreme,
               object_cols):
    parts = []
    if c in log_transform:
        parts.append("log1p")
    if c in extreme:
        parts.append("cap at P99.9")
    if c == "DAYS_EMPLOYED":
        parts.append("sentinel 365243 -> NaN")
    if c in high_card:
        parts.append("rare-merge + target encode")
    elif c in object_cols and c not in sparse_cat:
        parts.append("rare-merge + label encode")
    if c in sparse_cont or c in sparse_cat:
        parts.append("missing indicator + bin")
    return "; ".join(parts)


if __name__ == "__main__":
    main()
