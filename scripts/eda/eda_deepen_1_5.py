"""Deepen EDA steps 1-5 for application_train.

Completes the gaps left by the baseline profile (results/a/*):
  step 2 -- semantic types (binary flags vs low-cardinality ints vs continuous)
  step 3 -- missing patterns (row-level, co-missing block, missing vs target)
  step 5 -- target integrity (leakage guard)

Run: python scripts/eda_deepen_1_5.py
Output: results/eda/step1_5_deepen.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "data/raw/application_train.csv"
OUT = ROOT / "results/eda/step1_5_deepen.json"

KEY, TARGET = "SK_ID_CURR", "TARGET"


def main():
    train = pd.read_csv(TRAIN, low_memory=False)
    feats = [c for c in train.columns if c not in (KEY, TARGET)]
    num = [c for c in feats if str(train[c].dtype) != "object"]
    cat = [c for c in feats if str(train[c].dtype) == "object"]
    out = {}

    # --- step 2: semantic types among the 104 "numeric" features ---
    nun = train[num].nunique(dropna=True)
    binary = sorted(c for c in num if nun[c] == 2)
    lowcard = sorted(c for c in num if 2 < nun[c] <= 20)
    cont = sorted(c for c in num if nun[c] > 20)
    out["step2_semantic_types"] = {
        "numeric_total": len(num),
        "categorical_object": len(cat),
        "binary_flags": {"n": len(binary), "names": binary},
        "low_cardinality_int": {"n": len(lowcard), "names": {c: int(nun[c]) for c in lowcard}},
        "continuous": {"n": len(cont), "names": cont},
    }

    # --- step 3: missing patterns ---
    row_missing = train.isna().sum(axis=1)
    out["step3_missing"] = {
        "row_missing_count": {
            "min": int(row_missing.min()),
            "median": int(row_missing.median()),
            "mean": round(float(row_missing.mean()), 2),
            "max": int(row_missing.max()),
            "pct_fully_complete": round(float((row_missing == 0).mean()) * 100, 2),
        }
    }

    miss_rate = train.isna().mean()
    block_cols = [
        c for c in train.columns
        if 0.4 < miss_rate[c] < 0.8
        and not c.startswith("EXT_SOURCE")
        and c != "OCCUPATION_TYPE"
    ]
    block_missing = train[block_cols].isna().sum(axis=1)
    n_block = len(block_cols)
    out["step3_missing"]["sparse_block"] = {
        "n_columns": n_block,
        "columns": block_cols,
        "pct_rows_with_0_missing": round(float((block_missing == 0).mean()) * 100, 2),
        "pct_rows_with_all_missing": round(float((block_missing == n_block).mean()) * 100, 2),
        "pct_rows_missing_more_than_half": round(float((block_missing > n_block / 2).mean()) * 100, 2),
    }

    missing_vs_target = {}
    for col in ["EXT_SOURCE_1", "EXT_SOURCE_3", "EXT_SOURCE_2", "OCCUPATION_TYPE", "AMT_ANNUITY"]:
        miss = train[col].isna()
        missing_vs_target[col] = {
            "n_missing": int(miss.sum()),
            "pct_missing": round(float(miss.mean()) * 100, 2),
            "default_rate_missing": round(float(train.loc[miss, TARGET].mean()) * 100, 3),
            "default_rate_present": round(float(train.loc[~miss, TARGET].mean()) * 100, 3),
        }
    block_any = block_missing > 0
    missing_vs_target["sparse_block"] = {
        "n_missing": int(block_any.sum()),
        "pct_missing": round(float(block_any.mean()) * 100, 2),
        "default_rate_missing": round(float(train.loc[block_any, TARGET].mean()) * 100, 3),
        "default_rate_present": round(float(train.loc[~block_any, TARGET].mean()) * 100, 3),
    }
    out["step3_missing"]["missing_vs_target"] = missing_vs_target

    # --- step 5: target integrity / leakage guard ---
    corr = train[num + [TARGET]].corr()[TARGET].drop(TARGET)
    top = corr.abs().sort_values(ascending=False).head(8)
    out["step5_target_integrity"] = {
        "max_abs_corr_with_target": round(float(corr.abs().max()), 4),
        "top8_abs_corr": {c: round(float(v), 4) for c, v in top.items()},
        "features_identical_to_target": [
            c for c in num
            if train[c].equals(train[TARGET]) or train[c].equals(1 - train[TARGET])
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
