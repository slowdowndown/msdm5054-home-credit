"""Verify SHU's V0 data profile (results/baseline/*) against the raw data.

Recomputes the key facts in quality.json and field_profile.csv from
data/raw/application_train.csv (and application_test.csv), reports any
mismatch, and computes supplement stats the report's data overview needs.

Run: python scripts/verify_data_profile.py

Outputs:
  results/eda/data_profile_verify.json  -- per-check pass/fail + supplements
  results/eda/numeric_summary.csv       -- mean/std/min/median/max/skew per numeric feature
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

TRAIN = ROOT / "data/raw/application_train.csv"
TEST = ROOT / "data/raw/application_test.csv"
QA = ROOT / "results/baseline/quality.json"
PROFILE = ROOT / "results/baseline/field_profile.csv"
OUT_DIR = ROOT / "results/eda"

TOL = 1e-6


def is_cat(s):
    return str(s) == "object"


def main():
    train = pd.read_csv(TRAIN, low_memory=False)
    test = pd.read_csv(TEST, low_memory=False)
    qa = json.loads(QA.read_text(encoding="utf-8"))
    profile = pd.read_csv(PROFILE, encoding="utf-8-sig")

    report = []

    def check(name, got, want):
        if isinstance(want, bool):
            got_o, want_o, ok = bool(got), want, bool(got) == want
        elif isinstance(want, str):
            got_o, want_o, ok = str(got), want, str(got) == want
        elif isinstance(want, (int, np.integer)):
            got_o, want_o, ok = int(got), int(want), int(got) == int(want)
        else:
            got_o, want_o, ok = float(got), float(want), abs(float(got) - float(want)) <= TOL
        report.append({"check": name, "got": got_o, "want": want_o, "ok": bool(ok)})

    # --- quality.json ---
    check("train_rows", len(train), qa["train_rows"])
    check("train_columns", train.shape[1], qa["train_columns"])
    check("test_rows", len(test), qa["test_rows"])
    check("test_columns", test.shape[1], qa["test_columns"])
    check("duplicate_train_ids", train["SK_ID_CURR"].duplicated().sum(), qa["duplicate_train_ids"])
    check("duplicate_train_rows", train.duplicated().sum(), qa["duplicate_train_rows"])
    check(
        "train_test_id_overlap",
        len(set(train["SK_ID_CURR"]) & set(test["SK_ID_CURR"])),
        qa["train_test_id_overlap"],
    )
    check("target_missing", train["TARGET"].isna().sum(), qa["target_missing"])
    check("positive_count", (train["TARGET"] == 1).sum(), qa["positive_count"])
    check("positive_rate", (train["TARGET"] == 1).mean(), qa["positive_rate"])
    check("employment_365243", (train["DAYS_EMPLOYED"] == 365243).sum(), qa["employment_365243"])
    check("max_income", train["AMT_INCOME_TOTAL"].max(), qa["max_income"])

    feats = [c for c in train.columns if c not in ("SK_ID_CURR", "TARGET")]
    n_cat = sum(is_cat(train[c].dtype) for c in feats)
    n_num = len(feats) - n_cat
    check("categorical_features", n_cat, qa["categorical_features"])
    check("numeric_features", n_num, qa["numeric_features"])

    # --- field_profile.csv ---
    prof_map = {r["feature"]: r for _, r in profile.iterrows()}
    n_checked = 0
    n_mismatch = 0
    for c in train.columns:
        if c not in prof_map:
            continue
        n_checked += 1
        got_missing = int(train[c].isna().sum())
        got_rate = float(train[c].isna().mean())
        got_dtype = str(train[c].dtype)
        want_missing = int(prof_map[c]["missing_count"])
        want_rate = float(prof_map[c]["missing_rate"])
        want_dtype = str(prof_map[c]["dtype"])
        if got_missing != want_missing or abs(got_rate - want_rate) > TOL or got_dtype != want_dtype:
            n_mismatch += 1
            report.append(
                {
                    "check": f"field_profile:{c}",
                    "got": [got_dtype, got_missing, round(got_rate, 6)],
                    "want": [want_dtype, want_missing, round(want_rate, 6)],
                    "ok": False,
                }
            )
    report.append(
        {
            "check": "field_profile:all_columns",
            "got": f"{n_checked - n_mismatch} match / {n_mismatch} mismatch",
            "want": "all match",
            "ok": n_mismatch == 0,
        }
    )

    # --- supplements (not in the three files) ---
    missing_rate = train.isna().mean()
    supp = {}
    supp["columns_missing_gt80pct"] = int((missing_rate > 0.8).sum())
    supp["columns_missing_gt80pct_names"] = sorted(train.columns[missing_rate > 0.8].tolist())
    supp["constant_columns"] = [c for c in train.columns if train[c].nunique(dropna=True) == 1]

    emp = train["DAYS_EMPLOYED"]
    sentinel = train[emp == 365243]
    normal = train[emp != 365243]
    supp["employment_sentinel"] = {
        "n": int(len(sentinel)),
        "default_rate": float(sentinel["TARGET"].mean()),
    }
    supp["employment_normal"] = {
        "n": int(len(normal)),
        "default_rate": float(normal["TARGET"].mean()),
    }

    cat_card = {c: int(train[c].nunique()) for c in feats if is_cat(train[c].dtype)}
    supp["top_categorical_cardinality"] = dict(
        sorted(cat_card.items(), key=lambda kv: -kv[1])[:8]
    )

    # numeric summary for the distribution step
    num_feats = [c for c in feats if not is_cat(train[c].dtype)]
    summ = train[num_feats].agg(["mean", "std", "min", "median", "max", "skew"]).T
    summ.index.name = "feature"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summ.reset_index().to_csv(OUT_DIR / "numeric_summary.csv", index=False)

    result = {"verification": report, "supplements": supp}
    (OUT_DIR / "data_profile_verify.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    fails = [r for r in report if not r["ok"]]
    print(f"verification: {len(report) - len(fails)}/{len(report)} checks passed")
    for r in fails:
        print("  FAIL", r["check"], "got=", r["got"], "want=", r["want"])
    print("\nsupplements:")
    print(json.dumps(supp, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
