"""Derived ratio features for ratio-intrinsic columns (EDA step 8, groups 1-4).

Some application_train columns are only meaningful as a ratio (an amount
relative to income, a default count relative to the observed count, a duration
relative to age). The raw value is confounded by scale, so it is screened here
as the ratio, on the same footing as the raw columns. The 11 ratios cover four
groups:

    loan structure   CREDIT_TO_INCOME, ANNUITY_TO_INCOME, ANNUITY_TO_CREDIT,
                     CREDIT_TO_GOODS
    social circle    DEF30_TO_OBS30, DEF60_TO_OBS60
    family           INCOME_PER_MEMBER, CHILDREN_TO_FAMILY
    life cycle       EMPLOYED_TO_AGE, REGISTRATION_TO_AGE, ID_TO_AGE

Zero denominators (OBS_* = 0, AMT_GOODS_PRICE = 0 for cash loans) and the
DAYS_EMPLOYED = 365243 sentinel become NaN, which the WoE binner keeps as its
own "Missing" bin (a genuine group, not data loss).

All statistics are computed on the 80% train fold of the fixed split only.

Run: python scripts/eda_derived_iv.py
Output:
    results/eda/derived_iv_ranking.csv
    results/eda/derived_association.csv
    results/eda/woe_bins_derived.json
    results/eda/iv_ranking_all.csv      (raw + derived, sorted by IV)
    results/eda/association_all.csv     (raw + derived, sorted by |assoc|)
"""
import json
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "eda"))

import numpy as np
import pandas as pd

from eda_relationships import (
    woe_iv, point_biserial, cramers_v, feature_kind, SENTINEL_EMPLOYED,
)
from data_pipeline import fixed_split

KEY, TARGET = "SK_ID_CURR", "TARGET"

warnings.filterwarnings("ignore", category=RuntimeWarning)

# Each derived feature maps to its raw parents, used to judge whether the ratio
# improves on the columns it is built from.
PARENTS = {
    "CREDIT_TO_INCOME": ["AMT_CREDIT", "AMT_INCOME_TOTAL"],
    "ANNUITY_TO_INCOME": ["AMT_ANNUITY", "AMT_INCOME_TOTAL"],
    "ANNUITY_TO_CREDIT": ["AMT_ANNUITY", "AMT_CREDIT"],
    "CREDIT_TO_GOODS": ["AMT_CREDIT", "AMT_GOODS_PRICE"],
    "DEF30_TO_OBS30": ["DEF_30_CNT_SOCIAL_CIRCLE", "OBS_30_CNT_SOCIAL_CIRCLE"],
    "DEF60_TO_OBS60": ["DEF_60_CNT_SOCIAL_CIRCLE", "OBS_60_CNT_SOCIAL_CIRCLE"],
    "INCOME_PER_MEMBER": ["AMT_INCOME_TOTAL", "CNT_FAM_MEMBERS"],
    "CHILDREN_TO_FAMILY": ["CNT_CHILDREN", "CNT_FAM_MEMBERS"],
    "EMPLOYED_TO_AGE": ["DAYS_EMPLOYED", "DAYS_BIRTH"],
    "REGISTRATION_TO_AGE": ["DAYS_REGISTRATION", "DAYS_BIRTH"],
    "ID_TO_AGE": ["DAYS_ID_PUBLISH", "DAYS_BIRTH"],
}


def safe_div(num, den):
    """num / den with a zero denominator mapped to NaN (-> 'Missing' bin)."""
    return num / den.replace(0, np.nan)


def build_derived(tr):
    d = {}
    # loan structure
    d["CREDIT_TO_INCOME"] = safe_div(tr["AMT_CREDIT"], tr["AMT_INCOME_TOTAL"])
    d["ANNUITY_TO_INCOME"] = safe_div(tr["AMT_ANNUITY"], tr["AMT_INCOME_TOTAL"])
    d["ANNUITY_TO_CREDIT"] = safe_div(tr["AMT_ANNUITY"], tr["AMT_CREDIT"])
    d["CREDIT_TO_GOODS"] = safe_div(tr["AMT_CREDIT"], tr["AMT_GOODS_PRICE"])
    # social circle default intensity
    d["DEF30_TO_OBS30"] = safe_div(
        tr["DEF_30_CNT_SOCIAL_CIRCLE"], tr["OBS_30_CNT_SOCIAL_CIRCLE"])
    d["DEF60_TO_OBS60"] = safe_div(
        tr["DEF_60_CNT_SOCIAL_CIRCLE"], tr["OBS_60_CNT_SOCIAL_CIRCLE"])
    # family per-capita / dependency
    d["INCOME_PER_MEMBER"] = safe_div(tr["AMT_INCOME_TOTAL"], tr["CNT_FAM_MEMBERS"])
    d["CHILDREN_TO_FAMILY"] = safe_div(tr["CNT_CHILDREN"], tr["CNT_FAM_MEMBERS"])
    # life cycle (DAYS_BIRTH is negative, so both signs match and the ratio is
    # a positive fraction of life; the employment sentinel becomes NaN)
    d["EMPLOYED_TO_AGE"] = (
        tr["DAYS_EMPLOYED"].where(tr["DAYS_EMPLOYED"] < SENTINEL_EMPLOYED)
        / tr["DAYS_BIRTH"])
    d["REGISTRATION_TO_AGE"] = tr["DAYS_REGISTRATION"] / tr["DAYS_BIRTH"]
    d["ID_TO_AGE"] = tr["DAYS_ID_PUBLISH"] / tr["DAYS_BIRTH"]
    return pd.DataFrame(d)


def main():
    df = pd.read_csv(ROOT / "data/raw/application_train.csv", low_memory=False)
    fit_idx, _, _ = fixed_split(ROOT, train=df)
    tr = df.iloc[fit_idx].reset_index(drop=True)
    y = tr[TARGET].astype(int)

    derived = build_derived(tr)

    # ---- association ----
    assoc_rows = []
    for c in derived.columns:
        assoc_rows.append({
            "feature": c, "type": "numeric", "method": "point_biserial",
            "association": point_biserial(derived[c], y),
        })
    assoc = pd.DataFrame(assoc_rows)
    assoc["abs_association"] = assoc["association"].abs()
    assoc = assoc.sort_values("abs_association", ascending=False)
    assoc.to_csv(ROOT / "results/eda/derived_association.csv", index=False)

    # ---- WoE / IV ----
    nun = derived.nunique(dropna=True)
    iv_rows = []
    woe_out = {}
    for c in derived.columns:
        kind = feature_kind(derived[c], int(nun[c]))
        table, iv, mono, direction = woe_iv(derived[c], y, kind)
        iv_rows.append({"feature": c, "type": kind, "n_bins": int(len(table)),
                        "iv": round(iv, 4), "monotonic": mono,
                        "direction": direction})
        woe_out[c] = {
            "type": kind, "iv": round(iv, 4), "monotonic": mono,
            "direction": direction,
            "bins": table[["bin", "order", "n", "bad", "bad_rate", "woe", "iv"]]
                    .to_dict(orient="records"),
        }
    iv_derived = pd.DataFrame(iv_rows).sort_values("iv", ascending=False)
    iv_derived.to_csv(ROOT / "results/eda/derived_iv_ranking.csv", index=False)

    with open(ROOT / "results/eda/woe_bins_derived.json", "w", encoding="utf-8") as f:
        json.dump(woe_out, f, ensure_ascii=False, indent=2, default=lambda o: None
                  if isinstance(o, float) and (np.isnan(o) or np.isinf(o)) else o)

    # ---- merged rankings (raw + derived) ----
    raw_iv = pd.read_csv(ROOT / "results/eda/iv_ranking.csv")
    raw_assoc = pd.read_csv(ROOT / "results/eda/univariate_association.csv")
    iv_all = pd.concat([raw_iv, iv_derived], ignore_index=True).sort_values(
        "iv", ascending=False)
    assoc_all = pd.concat([raw_assoc, assoc], ignore_index=True).sort_values(
        "abs_association", ascending=False)
    iv_all.to_csv(ROOT / "results/eda/iv_ranking_all.csv", index=False)
    assoc_all.to_csv(ROOT / "results/eda/association_all.csv", index=False)

    # ---- comparison: ratio vs best parent ----
    raw_iv_map = dict(zip(raw_iv["feature"], raw_iv["iv"]))
    print("=== derived IV vs parents ===")
    for c in derived.columns:
        p_iv = {p: raw_iv_map.get(p, np.nan) for p in PARENTS[c]}
        best_parent = max(p_iv.values())
        win = "WIN " if iv_derived.loc[iv_derived.feature == c, "iv"].iloc[0] > best_parent else "    "
        print(f"{win}{c:22s} IV {iv_derived.loc[iv_derived.feature == c, 'iv'].iloc[0]:.4f}"
              f"  | parents {p_iv}")

    print("\n=== derived IV ranking (all) ===")
    print(iv_derived.to_string(index=False))
    print("\n=== merged top 25 IV ===")
    print(iv_all.head(25).to_string(index=False))


if __name__ == "__main__":
    main()
