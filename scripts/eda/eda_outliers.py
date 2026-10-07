"""Outlier and rare-category analysis for application_train (EDA step 7).

Systematically flags extreme upper-tail values across continuous columns, then
investigates the anomalies named in the plan (income 1.17e8, age > 100, and the
loan/annuity ratio) to judge whether each is a data error or a genuine rare
event. Also lists rare categorical levels. No rows are dropped here; the output
only quantifies the tails so treatment can be decided in feature engineering.

Run: python scripts/eda_outliers.py
Output: results/eda/outliers.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "data/raw/application_train.csv"
OUT = ROOT / "results/eda/outliers.json"

KEY, TARGET = "SK_ID_CURR", "TARGET"


def tail_profile(x):
    """Quantify the upper tail of a numeric series (dropna internally)."""
    x = x.dropna()
    p99 = float(x.quantile(0.99))
    p999 = float(x.quantile(0.999))
    return {
        "n": int(len(x)),
        "min": float(x.min()),
        "p50": float(x.median()),
        "p99": round(p99, 4),
        "p999": round(p999, 4),
        "max": float(x.max()),
        "n_gt_p99": int((x > p99).sum()),
        "max_over_p99": round(float(x.max()) / p99, 1) if p99 > 0 else None,
    }


def main():
    df = pd.read_csv(TRAIN, low_memory=False)
    feats = [c for c in df.columns if c not in (KEY, TARGET)]
    num = [c for c in feats if str(df[c].dtype) != "object"]
    obj = [c for c in feats if str(df[c].dtype) == "object"]
    nun = df[num].nunique(dropna=True)
    # non-binary numeric columns (counts/ordinals + continuous); binary flags
    # (nunique == 2) are excluded because their max/99th-percentile ratio is 1.
    cont = [c for c in num if nun[c] >= 3]
    out = {}

    # --- 1) systematic: columns whose max sits >= 5x above the 99th percentile
    tail = {}
    for c in cont:
        p = tail_profile(df[c])
        if p["max_over_p99"] is not None and p["max_over_p99"] >= 5:
            tail[c] = p
    out["tail_max_over_p99_ge_5"] = dict(
        sorted(tail.items(), key=lambda kv: -kv[1]["max_over_p99"]))

    # --- 2) named anomalies ---
    # income
    inc = df["AMT_INCOME_TOTAL"]
    out["income_amt"] = {
        **tail_profile(inc),
        "n_gt_1e6": int((inc > 1e6).sum()),
        "n_gt_5e6": int((inc > 5e6).sum()),
        "n_gt_1e7": int((inc > 1e7).sum()),
        "top10": [int(v) for v in inc.nlargest(10)],
    }

    # age (negative days before application -> years)
    age = -df["DAYS_BIRTH"] / 365.25
    out["age_years"] = {
        "min": round(float(age.min()), 2),
        "median": round(float(age.median()), 2),
        "max": round(float(age.max()), 2),
        "n_gt_100": int((age > 100).sum()),
        "n_gt_90": int((age > 90).sum()),
        "n_gt_80": int((age > 80).sum()),
        "n_gt_75": int((age > 75).sum()),
        "oldest10": [round(float(v), 1) for v in age.nlargest(10)],
    }

    # loan / annuity ratio (approx. repayment years)
    ratio = df["AMT_CREDIT"] / df["AMT_ANNUITY"]
    ratio = ratio.replace([np.inf, -np.inf], np.nan)
    out["annuity_ratio"] = {
        **tail_profile(ratio),
        "n_gt_50": int((ratio > 50).sum()),
        "n_gt_100": int((ratio > 100).sum()),
        "n_gt_200": int((ratio > 200).sum()),
        "top10": [round(float(v), 1) for v in ratio.nlargest(10)],
    }

    # --- 3) rare categorical levels (< 0.5% of rows) ---
    rare = {}
    for c in obj:
        vc = df[c].value_counts(dropna=True)
        n = int(len(df))
        rare_lv = {str(k): {"n": int(v), "pct": round(v / n * 100, 3)}
                   for k, v in vc.items() if v / n < 0.005}
        if rare_lv:
            entry = {
                "n_levels": int(len(vc)),
                "n_levels_lt_0p5pct": len(rare_lv),
                "share_lt_0p5pct": round(sum(v / n for v in vc if v / n < 0.005) * 100, 3),
            }
            # list the rare levels only when there are few (low-cardinality case);
            # high-cardinality columns report counts instead of enumerating.
            if len(rare_lv) <= 8:
                entry["rare_levels"] = rare_lv
            rare[c] = entry
    out["rare_categories"] = rare

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
