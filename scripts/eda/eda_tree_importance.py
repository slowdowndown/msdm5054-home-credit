"""Tree-model feature importance (EDA step 8, C2).

Trains a histogram-gradient-boosting classifier (sklearn, no external
dependency; native NaN and categorical handling) on the 80% train fold and
reports permutation importance. The point of C2 is to cross-check the IV
ranking: IV is a univariate, monotone measure, while tree importance also
surfaces nonlinear and interactive signal that IV misses.

DAYS_EMPLOYED = 365243 is set to NaN first so the unemployed sentinel is treated
as its own (missing) group, consistent with the WoE/IV screen. No log transform
is applied -- trees are invariant to monotone rescaling.

Permutation importance is computed on a 40,000-row subsample of the train fold
(n_repeats=3) to keep it fast; it is a relative ranking, not a validation score.

Run: python scripts/eda_tree_importance.py
Output:
    results/eda/tree_importance.csv
    results/eda/importance_iv_crosscheck.csv
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from data_pipeline import fixed_split

KEY, TARGET = "SK_ID_CURR", "TARGET"
SENTINEL = 365243

warnings.filterwarnings("ignore", category=RuntimeWarning)


def main():
    df = pd.read_csv(ROOT / "data/raw/application_train.csv", low_memory=False)
    fit_idx, _, _ = fixed_split(ROOT, train=df)
    tr = df.iloc[fit_idx].reset_index(drop=True)
    y = tr[TARGET].astype(int)
    feats = [c for c in df.columns if c not in (KEY, TARGET)]

    X = tr[feats].copy()
    X["DAYS_EMPLOYED"] = X["DAYS_EMPLOYED"].where(X["DAYS_EMPLOYED"] < SENTINEL)

    cat_cols = [c for c in feats if str(X[c].dtype) == "object"]
    cat_idx = [feats.index(c) for c in cat_cols]
    for c in cat_cols:
        X[c] = X[c].astype("category").cat.codes.replace(-1, np.nan)

    model = HistGradientBoostingClassifier(
        categorical_features=cat_idx,
        learning_rate=0.1,
        max_iter=150,
        max_leaf_nodes=31,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=10,
        random_state=42,
    )
    model.fit(X, y)

    rng = np.random.default_rng(42)
    idx = rng.choice(len(tr), size=40000, replace=False)
    pi = permutation_importance(
        model, X.iloc[idx], y.iloc[idx], n_repeats=3, random_state=42,
        scoring="roc_auc", n_jobs=1,
    )

    imp = pd.DataFrame({
        "feature": feats,
        "importance_mean": pi.importances_mean,
        "importance_std": pi.importances_std,
    }).sort_values("importance_mean", ascending=False)
    imp.to_csv(ROOT / "results/eda/tree_importance.csv", index=False)

    iv = pd.read_csv(ROOT / "results/eda/iv_ranking.csv")
    merged = imp.merge(iv[["feature", "iv", "type", "monotonic"]], on="feature",
                       how="left")
    merged.to_csv(ROOT / "results/eda/importance_iv_crosscheck.csv", index=False)

    print("=== top 30 tree importance (vs IV) ===")
    print(merged.head(30)[["feature", "importance_mean", "iv"]].to_string(index=False))
    print("\nrank correlation (Spearman) between importance and IV:",
          round(merged[["importance_mean", "iv"]].corr(method="spearman").iloc[0, 1], 4))


if __name__ == "__main__":
    main()
