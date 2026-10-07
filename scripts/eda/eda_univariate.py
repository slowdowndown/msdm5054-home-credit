"""Univariate profile and decisions for all 120 feature columns.

Completes EDA step 6 (univariate distributions): turns the descriptive plots
into a per-column profile -- distribution shape, anomalies, near-constant flag
-- plus a suggested modeling action. This is the machine-readable half of the
"field-level understanding" deliverable.

Run: python scripts/eda_univariate.py
Output:
    results/eda/univariate_summary.csv   one row per feature column
    results/eda/univariate_flags.json    grouped flags (near-constant, outliers, ...)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "data/raw/application_train.csv"
OUT_CSV = ROOT / "results/eda/univariate_summary.csv"
OUT_JSON = ROOT / "results/eda/univariate_flags.json"

KEY, TARGET = "SK_ID_CURR", "TARGET"


def semantic_type(s):
    if pd.api.types.is_numeric_dtype(s):
        nun = s.dropna().nunique()
        if nun == 2:
            return "binary"
        if nun <= 20:
            return "ordinal"
        return "continuous"
    return "categorical"


def describe(s):
    n = len(s)
    nn = s.dropna()
    nun = int(nn.nunique())
    row = {
        "missing_rate": round(float(s.isna().mean()), 4),
        "n_unique": nun,
        "top_share": round(float(nn.value_counts(normalize=True).iloc[0]), 4)
        if len(nn) else 1.0,
    }
    if pd.api.types.is_numeric_dtype(s):
        row.update({
            "min": float(nn.min()) if len(nn) else np.nan,
            "median": float(nn.median()) if len(nn) else np.nan,
            "p99": float(nn.quantile(0.99)) if len(nn) else np.nan,
            "max": float(nn.max()) if len(nn) else np.nan,
            "skew": round(float(nn.skew()), 3) if len(nn) else np.nan,
            "pct_zero": round(float((nn == 0).mean()), 4) if len(nn) else np.nan,
        })
    return row


def action_hint(t, row):
    if row["top_share"] >= 0.99:
        return "drop_near_constant"
    if t == "binary":
        return "keep_flag"
    if t == "ordinal":
        return "keep_ordinal"
    if t == "categorical":
        if row["missing_rate"] > 0.4:
            return "sparse_categorical"
        return "keep_categorical" if row["n_unique"] <= 15 else "high_cardinality"
    # continuous
    if row["missing_rate"] > 0.4:
        return "sparse_continuous"
    if row["skew"] > 2 and row["min"] > 0:
        return "log_transform"
    return "keep_numeric"


def main():
    df = pd.read_csv(TRAIN, low_memory=False)
    feats = [c for c in df.columns if c not in (KEY, TARGET)]

    rows = []
    for c in feats:
        t = semantic_type(df[c])
        r = describe(df[c])
        r.update({"feature": c, "type": t})
        r["action_hint"] = action_hint(t, r)
        rows.append(r)

    summary = pd.DataFrame(rows).set_index("feature")
    order = ["type", "action_hint", "missing_rate", "n_unique", "top_share",
             "min", "median", "p99", "max", "skew", "pct_zero"]
    summary = summary[order].sort_values(["action_hint", "type", "feature"])

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_CSV)

    flags = {
        "n_features": len(feats),
        "near_constant": sorted(summary[summary.action_hint == "drop_near_constant"].index),
        "log_transform": sorted(summary[summary.action_hint == "log_transform"].index),
        "high_cardinality": sorted(summary[summary.action_hint == "high_cardinality"].index),
        "sparse_continuous": sorted(summary[summary.action_hint == "sparse_continuous"].index),
        "sparse_categorical": sorted(summary[summary.action_hint == "sparse_categorical"].index),
        "extreme_outlier": sorted(
            c for c in summary.index
            if pd.notna(summary.loc[c, "p99"]) and pd.notna(summary.loc[c, "max"])
            and summary.loc[c, "p99"] > 0
            and summary.loc[c, "max"] > 20 * summary.loc[c, "p99"]
        ),
    }
    OUT_JSON.write_text(json.dumps(flags, ensure_ascii=False, indent=2), encoding="utf-8")

    print("features:", flags["n_features"])
    for k in ["near_constant", "log_transform", "high_cardinality",
              "extreme_outlier", "sparse_continuous", "sparse_categorical"]:
        print(f"{k} ({len(flags[k])}):", flags[k])


if __name__ == "__main__":
    main()
