"""Relationship analysis (EDA step 8, A1-A3) on the train fold.

A3 -- global association with TARGET: point-biserial r for numeric columns and
      Cramer's V for categorical columns, one row per feature, ranked by
      magnitude.
A1 -- WoE/IV: equal-frequency bins for continuous columns, rare levels merged
      into "Other" for categorical columns; missing values and the
      DAYS_EMPLOYED = 365243 sentinel are kept as their own bins. IV is ranked
      across all 120 features.
A2 -- monotonicity of the default rate across ordered bins (continuous and
      ordinal columns).

All statistics are computed on the 80% train fold of the fixed split only; the
validation fold is never touched, so feature selection cannot leak into it.

Run: python scripts/eda_relationships.py
Output:
    results/eda/univariate_association.csv
    results/eda/iv_ranking.csv
    results/eda/woe_bins.json
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from data_pipeline import fixed_split

KEY, TARGET = "SK_ID_CURR", "TARGET"
SENTINEL_EMPLOYED = 365243
N_BINS = 10
MIN_BIN_COUNT = 1000

warnings.filterwarnings("ignore", category=RuntimeWarning)


def _json_default(o):
    if isinstance(o, float) and (np.isnan(o) or np.isinf(o)):
        return None
    if isinstance(o, np.generic):
        return o.item()
    raise TypeError


def cramers_v(x, y):
    ct = pd.crosstab(x, y)
    chi2 = chi2_contingency(ct, correction=False)[0]
    n = int(ct.to_numpy().sum())
    k = min(ct.shape) - 1
    return float(np.sqrt(chi2 / (n * k))) if k > 0 else 0.0


def point_biserial(x, y):
    m = x.notna() & y.notna()
    x, y = x[m], y[m]
    if len(x) < 2 or x.std() == 0:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def feature_kind(x, nunique):
    if str(x.dtype) == "object":
        return "nominal"
    if nunique == 2:
        return "nominal"
    if nunique <= 20:
        return "ordinal"
    return "continuous"


def woe_iv(x, y, kind):
    """Bin x; return (bin_table, iv, monotonic, direction)."""
    total_good = float((y == 0).sum())
    total_bad = float((y == 1).sum())
    missing = x.isna()

    if kind == "continuous":
        codes = pd.qcut(x, N_BINS, duplicates="drop", labels=False)
        if codes.nunique() < 3:  # degenerate after duplicate collapse
            labels = x.astype(str)
            kind = "ordinal"
        else:
            labels = codes.astype(str)
    else:
        labels = x.astype(str)

    labels = labels.where(~missing, "Missing")
    vc = labels.value_counts()
    rare = set(vc[vc < MIN_BIN_COUNT].index) - {"Missing"}
    labels = labels.where(~labels.isin(rare), "Other")

    tmp = pd.DataFrame({"bin": labels, "x": x, "y": y})
    rows = []
    iv = 0.0
    for b in sorted(labels.unique()):
        sub = tmp[tmp["bin"] == b]
        g = float((sub["y"] == 0).sum())
        d = float((sub["y"] == 1).sum())
        woe = np.log(((g + 0.5) / total_good) / ((d + 0.5) / total_bad))
        contrib = (g / total_good - d / total_bad) * woe
        iv += contrib
        order = (float(sub["x"].median())
                 if pd.api.types.is_numeric_dtype(sub["x"]) and sub["x"].notna().any()
                 else np.nan)
        rows.append({
            "bin": b, "order": order, "n": int(len(sub)), "bad": int(d),
            "bad_rate": round(d / len(sub), 4), "woe": round(woe, 4),
            "iv": round(contrib, 6),
        })
    table = pd.DataFrame(rows).sort_values("order", na_position="last")

    mono = None
    direction = None
    if kind in ("continuous", "ordinal"):
        ordered = table[~table["bin"].isin(["Missing", "Other"])].sort_values("order")
        if len(ordered) >= 3:
            br = ordered["bad_rate"].tolist()
            if all(a <= b for a, b in zip(br, br[1:])):
                mono, direction = True, "increasing"
            elif all(a >= b for a, b in zip(br, br[1:])):
                mono, direction = True, "decreasing"
            else:
                mono = False
    return table, iv, mono, direction


def main():
    df = pd.read_csv(ROOT / "data/raw/application_train.csv", low_memory=False)
    fit_idx, _, _ = fixed_split(ROOT, train=df)
    tr = df.iloc[fit_idx].reset_index(drop=True)
    y = tr[TARGET].astype(int)

    feats = [c for c in df.columns if c not in (KEY, TARGET)]
    nun = tr[feats].nunique(dropna=True)

    # ---- A3: global association ----
    assoc_rows = []
    for c in feats:
        if str(tr[c].dtype) == "object":
            assoc_rows.append({"feature": c, "type": "categorical",
                               "method": "cramers_v",
                               "association": cramers_v(tr[c], y)})
        elif c == "DAYS_EMPLOYED":
            x = tr[c].where(tr[c] < SENTINEL_EMPLOYED)
            assoc_rows.append({"feature": c, "type": "continuous",
                               "method": "point_biserial",
                               "association": point_biserial(x, y)})
            sent = (tr[c] == SENTINEL_EMPLOYED).astype(int)
            assoc_rows.append({"feature": "DAYS_EMPLOYED_365243",
                               "type": "derived_binary",
                               "method": "point_biserial",
                               "association": point_biserial(sent, y)})
        else:
            assoc_rows.append({"feature": c, "type": "numeric",
                               "method": "point_biserial",
                               "association": point_biserial(tr[c], y)})
    assoc = pd.DataFrame(assoc_rows)
    assoc["abs_association"] = assoc["association"].abs()
    assoc = assoc.sort_values("abs_association", ascending=False)
    assoc.to_csv(ROOT / "results/eda/univariate_association.csv", index=False)

    # ---- A1 + A2: WoE / IV ----
    iv_rows = []
    woe_out = {}
    for c in feats:
        if c == "DAYS_EMPLOYED":
            x = tr[c].where(tr[c] < SENTINEL_EMPLOYED)
            kind = "continuous"
        else:
            x = tr[c]
            kind = feature_kind(x, int(nun[c]))
        table, iv, mono, direction = woe_iv(x, y, kind)
        iv_rows.append({"feature": c, "type": kind, "n_bins": int(len(table)),
                        "iv": round(iv, 4), "monotonic": mono,
                        "direction": direction})
        woe_out[c] = {
            "type": kind, "iv": round(iv, 4), "monotonic": mono,
            "direction": direction,
            "bins": table[["bin", "order", "n", "bad", "bad_rate", "woe", "iv"]]
                    .to_dict(orient="records"),
        }
    iv_rank = pd.DataFrame(iv_rows).sort_values("iv", ascending=False)
    iv_rank.to_csv(ROOT / "results/eda/iv_ranking.csv", index=False)

    with open(ROOT / "results/eda/woe_bins.json", "w", encoding="utf-8") as f:
        json.dump(woe_out, f, ensure_ascii=False, indent=2, default=_json_default)

    print("=== A3 top 15 association ===")
    print(assoc.head(15).to_string(index=False))
    print("\n=== A1 top 20 IV ===")
    print(iv_rank.head(20).to_string(index=False))
    ord_cont = iv_rank[iv_rank.type.isin(["continuous", "ordinal"])]
    print("\nmonotonic (continuous/ordinal):",
          int((ord_cont.monotonic == True).sum()), "of", int(len(ord_cont)))


if __name__ == "__main__":
    main()
