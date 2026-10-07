"""Collinearity among numeric columns (EDA step 8, B1-B2).

B1 -- Spearman pairwise correlation on the non-binary numeric columns (robust to
      the heavy tails in AMT_* and the sparse building block). Pairs above 0.8
      are written out.
B2 -- cluster the |r| > 0.9 graph into collinearity groups and keep one
      representative per group (the highest-IV column from iv_ranking.csv); the
      rest are drop candidates.

All statistics are computed on the 80% train fold of the fixed split only.

Run: python scripts/eda_collinearity.py
Output:
    results/eda/correlation_matrix.csv      full Spearman matrix (cont columns)
    results/eda/correlation_pairs.csv       pairs with |r| > 0.8, sorted
    results/eda/collinearity_groups.json    groups at |r| > 0.9 + representative
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from data_pipeline import fixed_split

KEY, TARGET = "SK_ID_CURR", "TARGET"
PAIR_THRESHOLD = 0.8
GROUP_THRESHOLD = 0.9

warnings.filterwarnings("ignore", category=RuntimeWarning)


def connected_components(nodes, edges):
    adj = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    seen = set()
    groups = []
    for n in nodes:
        if n in seen:
            continue
        stack = [n]
        seen.add(n)
        comp = []
        while stack:
            cur = stack.pop()
            comp.append(cur)
            for nb in adj[cur]:
                if nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        groups.append(comp)
    return groups


def main():
    df = pd.read_csv(ROOT / "data/raw/application_train.csv", low_memory=False)
    fit_idx, _, _ = fixed_split(ROOT, train=df)
    tr = df.iloc[fit_idx].reset_index(drop=True)

    feats = [c for c in df.columns if c not in (KEY, TARGET)]
    num = [c for c in feats if str(tr[c].dtype) != "object"]
    nun = tr[num].nunique(dropna=True)
    # non-binary numeric columns: binary flags have degenerate variance and are
    # handled by the near-constant analysis, not by collinearity.
    cont = [c for c in num if nun[c] >= 3]

    corr = tr[cont].corr(method="spearman")

    # unique pairs, sorted by |r|
    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iloc[i, j]
            if pd.notna(r):
                pairs.append((cols[i], cols[j], float(r)))
    pairs.sort(key=lambda t: -abs(t[2]))

    corr.to_csv(ROOT / "results/eda/correlation_matrix.csv")

    pair_df = pd.DataFrame(pairs, columns=["a", "b", "spearman_r"])
    pair_df["abs_r"] = pair_df["spearman_r"].abs()
    pair_df[pair_df.abs_r > PAIR_THRESHOLD].to_csv(
        ROOT / "results/eda/correlation_pairs.csv", index=False)

    # cluster at GROUP_THRESHOLD
    edges = [(a, b) for a, b, r in pairs if abs(r) > GROUP_THRESHOLD]
    groups = connected_components(cont, edges)
    groups = [g for g in groups if len(g) >= 2]

    iv = pd.read_csv(ROOT / "results/eda/iv_ranking.csv")
    iv_map = dict(zip(iv["feature"], iv["iv"]))

    group_out = []
    for g in groups:
        rep = max(g, key=lambda c: iv_map.get(c, -1.0))
        members = sorted(g, key=lambda c: -iv_map.get(c, -1.0))
        group_out.append({
            "representative": rep,
            "representative_iv": round(iv_map.get(rep, float("nan")), 4),
            "drop": [c for c in members if c != rep],
            "n_members": len(members),
        })
    group_out.sort(key=lambda g: -g["representative_iv"])

    out = {
        "n_cont_columns": len(cont),
        "pair_threshold": PAIR_THRESHOLD,
        "group_threshold": GROUP_THRESHOLD,
        "n_groups": len(group_out),
        "n_dropped": sum(len(g["drop"]) for g in group_out),
        "groups": group_out,
    }
    (ROOT / "results/eda/collinearity_groups.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"cont columns: {len(cont)}")
    print(f"\n=== top 30 |r| pairs ===")
    print(pair_df.head(30).to_string(index=False))
    print(f"\n=== groups (|r| > {GROUP_THRESHOLD}) ===")
    for g in group_out:
        print(f"{g['representative']} (IV {g['representative_iv']})  <- "
              f"drop {g['drop']}")


if __name__ == "__main__":
    main()
