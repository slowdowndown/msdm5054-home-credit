"""Generate EDA figures for the Home Credit report.

Run from the repository root:

    python scripts/make_eda_figures.py

Figures are saved to results/eda/figures/ as PNG (preview) and PDF (report).
Step 6 (univariate distributions) dispatches each variable to the chart form
that matches its semantic type:

    continuous            -> histogram (log-x when heavily right-skewed)
    binary flag           -> horizontal proportion bars ("the number is the chart")
    low-cardinality count -> count bars (integer frequencies)
    categorical           -> horizontal top-N bars, tail folded into "Other"
    sparse building block -> missing-rate overview first, then examples

Extend make_all() as new figures are added.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "eda"))

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

from plotting import (
    set_style, new_figure, savefig, histogram,
    INK, GRAY_RAMP, GRID, TEXT_SECONDARY, compact_k,
    SINGLE_COL, DOUBLE_COL,
    hbar_topn, hbar_proportion, count_bars,
)

set_style()

TRAIN = ROOT / "data/raw/application_train.csv"
SENTINEL_EMPLOYED = 365243

CONTACT_FLAGS = [
    "FLAG_MOBIL", "FLAG_EMP_PHONE", "FLAG_WORK_PHONE", "FLAG_CONT_MOBILE",
    "FLAG_PHONE", "FLAG_EMAIL",
]
REGION_FLAGS = [
    "REG_REGION_NOT_LIVE_REGION", "REG_REGION_NOT_WORK_REGION",
    "LIVE_REGION_NOT_WORK_REGION", "REG_CITY_NOT_LIVE_CITY",
    "REG_CITY_NOT_WORK_CITY", "LIVE_CITY_NOT_WORK_CITY",
]
DOCUMENT_FLAGS = [f"FLAG_DOCUMENT_{i}" for i in
                  [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]]

SPARSE_BLOCK = [
    "OWN_CAR_AGE",
    "APARTMENTS_AVG", "BASEMENTAREA_AVG", "YEARS_BEGINEXPLUATATION_AVG", "YEARS_BUILD_AVG",
    "COMMONAREA_AVG", "ELEVATORS_AVG", "ENTRANCES_AVG", "FLOORSMAX_AVG", "FLOORSMIN_AVG",
    "LANDAREA_AVG", "LIVINGAPARTMENTS_AVG", "LIVINGAREA_AVG", "NONLIVINGAPARTMENTS_AVG",
    "NONLIVINGAREA_AVG",
    "APARTMENTS_MODE", "BASEMENTAREA_MODE", "YEARS_BEGINEXPLUATATION_MODE", "YEARS_BUILD_MODE",
    "COMMONAREA_MODE", "ELEVATORS_MODE", "ENTRANCES_MODE", "FLOORSMAX_MODE", "FLOORSMIN_MODE",
    "LANDAREA_MODE", "LIVINGAPARTMENTS_MODE", "LIVINGAREA_MODE", "NONLIVINGAPARTMENTS_MODE",
    "NONLIVINGAREA_MODE",
    "APARTMENTS_MEDI", "BASEMENTAREA_MEDI", "YEARS_BEGINEXPLUATATION_MEDI", "YEARS_BUILD_MEDI",
    "COMMONAREA_MEDI", "ELEVATORS_MEDI", "ENTRANCES_MEDI", "FLOORSMAX_MEDI", "FLOORSMIN_MEDI",
    "LANDAREA_MEDI", "LIVINGAPARTMENTS_MEDI", "LIVINGAREA_MEDI", "NONLIVINGAPARTMENTS_MEDI",
    "NONLIVINGAREA_MEDI",
    "FONDKAPREMONT_MODE", "HOUSETYPE_MODE", "TOTALAREA_MODE", "WALLSMATERIAL_MODE",
    "EMERGENCYSTATE_MODE",
]


def _load(cols):
    return pd.read_csv(TRAIN, usecols=cols, low_memory=False)


def _years(days):
    """Convert negative day offsets (days before application) to positive years."""
    return -np.asarray(days, dtype=float) / 365.25


# --- 00 target ---------------------------------------------------------------
def target_distribution():
    target = pd.read_csv(TRAIN, usecols=["TARGET"])
    vc = target["TARGET"].value_counts().sort_index()
    n = int(len(target))
    neg = int(vc.get(0, 0))
    pos = int(vc.get(1, 0))

    fig, ax = new_figure(SINGLE_COL, height=2.4)
    cats = ["TARGET = 0", "TARGET = 1"]
    vals = [neg, pos]
    colors = [GRAY_RAMP[4], INK]  # light gray vs ink (positive class stands out)

    bars = ax.bar(cats, vals, color=colors, width=0.5)
    for b, v in zip(bars, vals):
        pct = v / n * 100
        ax.annotate(
            f"{v:,}\n({pct:.1f}%)",
            (b.get_x() + b.get_width() / 2, b.get_height()),
            ha="center", va="bottom", xytext=(0, 3), textcoords="offset points",
            fontsize=9, color=INK,
        )

    ax.set_title("TARGET distribution")
    ax.set_ylabel("Count")
    ax.yaxis.set_major_formatter(compact_k)
    ax.grid(axis="y", color="#e3e3e3", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.margins(y=0.12)
    ax.set_ylim(0, neg * 1.28)
    ax.text(
        0.98, 0.94, f"positive rate {pos / n * 100:.2f}%\n(n = {n:,})",
        transform=ax.transAxes, ha="right", va="top", fontsize=8, color="#555555",
    )
    return savefig(fig, "00_target_distribution")


# --- 01 loan amounts ---------------------------------------------------------
def loan_amount_distributions():
    cols = ["AMT_CREDIT", "AMT_ANNUITY", "AMT_GOODS_PRICE"]
    df = _load(cols)

    fig, axes = plt.subplots(1, len(cols), figsize=(DOUBLE_COL, DOUBLE_COL * 0.36))
    for ax, col in zip(axes, cols):
        histogram(ax, df[col], logx=True)
        ax.set_title(col)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Count")
    fig.supxlabel("value (log scale)")
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.88, wspace=0.30)
    return savefig(fig, "01_loan_amount_distributions")


# --- 02 income ---------------------------------------------------------------
def income_distribution():
    df = _load(["AMT_INCOME_TOTAL"])
    fig, ax = new_figure(SINGLE_COL, height=2.4)
    histogram(ax, df["AMT_INCOME_TOTAL"], logx=True)
    ax.set_title("AMT_INCOME_TOTAL (income)")
    ax.set_ylabel("Count")
    ax.set_xlabel("income (log scale)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "02_income_distribution")


# --- 03 days -> years ---------------------------------------------------------
def days_to_years():
    cols = ["DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION",
            "DAYS_ID_PUBLISH", "DAYS_LAST_PHONE_CHANGE"]
    df = _load(cols)
    panels = [
        ("age", _years(df["DAYS_BIRTH"])),
        ("employment", _years(df.loc[df["DAYS_EMPLOYED"] < 0, "DAYS_EMPLOYED"])),
        ("registration", _years(df["DAYS_REGISTRATION"])),
        ("ID issued", _years(df["DAYS_ID_PUBLISH"])),
        ("phone change", _years(df["DAYS_LAST_PHONE_CHANGE"])),
    ]

    fig, axes = plt.subplots(1, 5, figsize=(DOUBLE_COL, 2.3))
    for ax, (label, vals) in zip(axes, panels):
        histogram(ax, vals)
        ax.set_title(label)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Count")
    axes[1].text(
        0.97, 0.92, "sentinel 365,243\n(18%) excluded",
        transform=axes[1].transAxes, ha="right", va="top",
        fontsize=6.5, color=TEXT_SECONDARY,
    )
    fig.supxlabel("years")
    fig.subplots_adjust(left=0.06, right=0.99, bottom=0.18, top=0.88, wspace=0.32)
    return savefig(fig, "03_days_to_years")


# --- 04 external sources ------------------------------------------------------
def ext_sources():
    df = _load(["EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3"])
    fig, axes = plt.subplots(1, 3, figsize=(DOUBLE_COL, 2.2))
    for ax, col in zip(axes, df.columns):
        histogram(ax, df[col])
        ax.set_title(col)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Count")
    fig.supxlabel("normalized score (0-1)")
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.86, wspace=0.30)
    return savefig(fig, "04_ext_sources")


# --- 05/06 binary flags (proportions) ----------------------------------------
def flags_contact_region():
    cols = CONTACT_FLAGS + REGION_FLAGS
    df = _load(cols)
    props = [df[c].mean() for c in cols]
    fig, ax = plt.subplots(figsize=(DOUBLE_COL, 3.4))
    hbar_proportion(ax, cols, props, xlabel="share of applications with flag = 1")
    ax.set_title("Contact and region-mismatch flags")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "05_flags_contact_region")


def flags_document():
    df = _load(DOCUMENT_FLAGS)
    props = [df[c].mean() for c in DOCUMENT_FLAGS]
    fig, ax = plt.subplots(figsize=(DOUBLE_COL, 4.6))
    hbar_proportion(ax, DOCUMENT_FLAGS, props, xlabel="share of applications with flag = 1")
    ax.set_title("Document flags")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "06_flags_document")


# --- 07 credit bureau requests ------------------------------------------------
def bureau_requests():
    cols = ["AMT_REQ_CREDIT_BUREAU_HOUR", "AMT_REQ_CREDIT_BUREAU_DAY",
            "AMT_REQ_CREDIT_BUREAU_WEEK", "AMT_REQ_CREDIT_BUREAU_MON",
            "AMT_REQ_CREDIT_BUREAU_QRT", "AMT_REQ_CREDIT_BUREAU_YEAR"]
    df = _load(cols)
    fig, axes = plt.subplots(2, 3, figsize=(DOUBLE_COL, 3.8))
    for ax, col in zip(axes.flat, cols):
        count_bars(ax, df[col], cap=12)
        ax.set_title(col.replace("AMT_REQ_CREDIT_BUREAU_", ""))
    for ax in axes[1]:
        ax.set_xlabel("enquiries in window")
    for ax in axes[:, 0]:
        ax.set_ylabel("Count")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "07_bureau_requests")


# --- 08 social circle ---------------------------------------------------------
def social_circle():
    cols = ["OBS_30_CNT_SOCIAL_CIRCLE", "OBS_60_CNT_SOCIAL_CIRCLE",
            "DEF_30_CNT_SOCIAL_CIRCLE", "DEF_60_CNT_SOCIAL_CIRCLE"]
    df = _load(cols)
    fig, axes = plt.subplots(1, 4, figsize=(DOUBLE_COL, 2.3))
    for ax, col in zip(axes, cols):
        count_bars(ax, df[col], cap=10)
        ax.set_title(col)
    axes[0].set_ylabel("Count")
    fig.supxlabel("count")
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.18, top=0.86, wspace=0.35)
    return savefig(fig, "08_social_circle")


# --- 09 children / family / region rating -------------------------------------
def children_family_rating():
    cols = ["CNT_CHILDREN", "CNT_FAM_MEMBERS",
            "REGION_RATING_CLIENT", "REGION_RATING_CLIENT_W_CITY"]
    df = _load(cols)
    fig, axes = plt.subplots(1, 4, figsize=(DOUBLE_COL, 2.3))
    for ax, col in zip(axes, cols):
        count_bars(ax, df[col], cap=12)
        ax.set_title(col)
    axes[0].set_ylabel("Count")
    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.18, top=0.86, wspace=0.35)
    return savefig(fig, "09_children_family_rating")


# --- 10/11 region population / car age ----------------------------------------
def region_population():
    df = _load(["REGION_POPULATION_RELATIVE"])
    fig, ax = new_figure(SINGLE_COL, height=2.4)
    histogram(ax, df["REGION_POPULATION_RELATIVE"], logx=True)
    ax.set_title("REGION_POPULATION_RELATIVE")
    ax.set_ylabel("Count")
    ax.set_xlabel("population share (log scale)")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "10_region_population")


def own_car_age():
    df = _load(["OWN_CAR_AGE"])
    fig, ax = new_figure(SINGLE_COL, height=2.4)
    histogram(ax, df["OWN_CAR_AGE"])
    ax.set_title("OWN_CAR_AGE (66% missing)")
    ax.set_ylabel("Count")
    ax.set_xlabel("car age (years)")
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "11_own_car_age")


# --- 12/13 categorical core ---------------------------------------------------
def categorical_demographic():
    cols = ["CODE_GENDER", "NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS"]
    df = _load(cols)
    fig, axes = plt.subplots(2, 2, figsize=(DOUBLE_COL, 5.0))
    for ax, col in zip(axes.flat, cols):
        hbar_topn(ax, df[col], topn=8)
        ax.set_title(col)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "12_categorical_demographic")


def categorical_housing_contract():
    cols = ["NAME_HOUSING_TYPE", "NAME_CONTRACT_TYPE", "NAME_TYPE_SUITE",
            "WEEKDAY_APPR_PROCESS_START"]
    df = _load(cols)
    fig, axes = plt.subplots(2, 2, figsize=(DOUBLE_COL, 5.0))
    for ax, col in zip(axes.flat, cols):
        hbar_topn(ax, df[col], topn=8)
        ax.set_title(col)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "13_categorical_housing_contract")


# --- 14 occupation / organization ---------------------------------------------
def occupation_organization():
    df = _load(["OCCUPATION_TYPE", "ORGANIZATION_TYPE"])
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL, 4.4))
    hbar_topn(axes[0], df["OCCUPATION_TYPE"], topn=18)
    axes[0].set_title("OCCUPATION_TYPE")
    hbar_topn(axes[1], df["ORGANIZATION_TYPE"], topn=15)
    axes[1].set_title("ORGANIZATION_TYPE (top 15 + other)")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "14_occupation_organization")


# --- 15 ownership flags (Y/N) --------------------------------------------------
def flags_own():
    cols = ["FLAG_OWN_CAR", "FLAG_OWN_REALTY"]
    df = _load(cols)
    props = [(df[c] == "Y").mean() for c in cols]
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 1.6))
    hbar_proportion(ax, cols, props, xlabel="share = 'Y'")
    ax.set_title("Ownership flags")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "15_flags_own")


# --- 16/17 sparse building block ----------------------------------------------
def sparse_block_missing():
    df = _load(SPARSE_BLOCK)
    rates = df.isna().mean().sort_values() * 100
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 8.5))
    y = np.arange(len(rates))
    ax.barh(y, rates.values, color=INK, height=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(rates.index, fontsize=5.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel("missing rate (%)")
    ax.set_title("Sparse building-region block: missing rate")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "16_sparse_block_missing")


def sparse_block_examples():
    cols = ["APARTMENTS_AVG", "LIVINGAREA_AVG", "YEARS_BUILD_AVG", "ELEVATORS_AVG"]
    df = _load(cols)
    fig, axes = plt.subplots(1, 4, figsize=(DOUBLE_COL, 2.2))
    for ax, col in zip(axes, cols):
        histogram(ax, df[col])
        ax.set_title(col.replace("_AVG", ""))
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Count")
    fig.supxlabel("normalized ratio (0-1)")
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.86, wspace=0.32)
    return savefig(fig, "17_sparse_block_examples")


# --- 18 application hour ------------------------------------------------------
def hour_appr_process():
    df = _load(["HOUR_APPR_PROCESS_START"])
    fig, ax = new_figure(SINGLE_COL, height=2.4)
    count_bars(ax, df["HOUR_APPR_PROCESS_START"], cap=24)
    ax.set_title("HOUR_APPR_PROCESS_START")
    ax.set_ylabel("Count")
    ax.set_xlabel("hour of day")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "18_hour_appr_process")


# --- 19/20/21 outliers (step 7) ----------------------------------------------
def outlier_income():
    df = _load(["AMT_INCOME_TOTAL"])
    x = df["AMT_INCOME_TOTAL"]
    p99, p999, mx = x.quantile(0.99), x.quantile(0.999), x.max()
    fig, ax = new_figure(SINGLE_COL, height=2.6)
    histogram(ax, x, logx=True)
    ax.set_title("AMT_INCOME_TOTAL (income)")
    ax.set_ylabel("Count")
    ax.set_xlabel("income (log scale)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.axvline(p99, color=TEXT_SECONDARY, linewidth=0.8, linestyle="--")
    ax.axvline(p999, color=TEXT_SECONDARY, linewidth=0.8, linestyle="--")
    ax.axvline(mx, color=INK, linewidth=0.8, linestyle="--")
    ax.text(0.02, 0.97,
            f"P99 = {p99:,.0f}\nP99.9 = {p999:,.0f}\nmax = {mx:,.0f}",
            transform=ax.transAxes, ha="left", va="top", fontsize=8, color=INK,
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8))
    fig.tight_layout(pad=0.4)
    return savefig(fig, "19_outlier_income")


def outlier_age_ratio():
    df = _load(["DAYS_BIRTH", "AMT_CREDIT", "AMT_ANNUITY"])
    age = _years(df["DAYS_BIRTH"])
    ratio = (df["AMT_CREDIT"] / df["AMT_ANNUITY"]).replace([np.inf, -np.inf], np.nan)
    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.3))
    histogram(axes[0], age)
    axes[0].set_title("age (years)")
    axes[0].grid(axis="y", color=GRID, linewidth=0.6)
    axes[0].set_axisbelow(True)
    histogram(axes[1], ratio)
    axes[1].set_title("credit / annuity (years)")
    axes[1].grid(axis="y", color=GRID, linewidth=0.6)
    axes[1].set_axisbelow(True)
    axes[0].set_ylabel("Count")
    axes[0].text(0.03, 0.95, f"max = {age.max():.1f}\n(no age > 100)",
                 transform=axes[0].transAxes, ha="left", va="top",
                 fontsize=7, color=TEXT_SECONDARY)
    axes[1].text(0.03, 0.95, f"max = {ratio.max():.1f}\n(no ratio > 50)",
                 transform=axes[1].transAxes, ha="left", va="top",
                 fontsize=7, color=TEXT_SECONDARY)
    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.18, top=0.86, wspace=0.32)
    return savefig(fig, "20_outlier_age_ratio")


def outlier_tail_ratio():
    cols = [
        "AMT_INCOME_TOTAL", "AMT_REQ_CREDIT_BUREAU_QRT",
        "OBS_30_CNT_SOCIAL_CIRCLE", "OBS_60_CNT_SOCIAL_CIRCLE",
        "DEF_30_CNT_SOCIAL_CIRCLE", "DEF_60_CNT_SOCIAL_CIRCLE",
        "AMT_REQ_CREDIT_BUREAU_WEEK", "AMT_REQ_CREDIT_BUREAU_MON",
        "CNT_CHILDREN",
    ]
    df = _load(cols)
    ratios = {c: df[c].max() / df[c].quantile(0.99) for c in cols}
    pairs = sorted(ratios.items(), key=lambda t: t[1])
    labels = [p[0] for p in pairs]
    vals = [p[1] for p in pairs]
    fig, ax = plt.subplots(figsize=(SINGLE_COL, 3.0))
    y = np.arange(len(labels))
    ax.barh(y, vals, color=INK, height=0.6)
    for yi, v in zip(y, vals):
        ax.text(v, yi, f" {v:.0f}x", va="center", fontsize=8,
                color=TEXT_SECONDARY)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.5)
    ax.set_xlabel("max / 99th percentile")
    ax.set_title("Extreme tail (count and amount columns)")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=0.4)
    return savefig(fig, "21_outlier_tail_ratio")


# --- 22/23/24 relationships (step 8) -----------------------------------------
_ASSOC = None
_IV = None
_WOE = None


def _load_relationship_results():
    global _ASSOC, _IV, _WOE
    if _ASSOC is None:
        _ASSOC = pd.read_csv(ROOT / "results/eda/univariate_association.csv")
        _IV = pd.read_csv(ROOT / "results/eda/iv_ranking.csv")
        with open(ROOT / "results/eda/woe_bins.json", encoding="utf-8") as f:
            _WOE = json.load(f)
    return _ASSOC, _IV, _WOE


def association_screening():
    assoc, _, _ = _load_relationship_results()
    numeric = assoc[(assoc.method == "point_biserial")
                    & ~assoc.feature.str.startswith("DAYS_EMPLOYED_365243")]
    numeric = numeric.nlargest(15, "abs_association").sort_values("abs_association")
    cat = assoc[assoc.method == "cramers_v"].nlargest(12, "abs_association").sort_values("abs_association")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.6))

    ax = axes[0]
    y = np.arange(len(numeric))
    ax.barh(y, numeric.abs_association.values, color=INK, height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels(numeric.feature.values, fontsize=7)
    ax.set_xlabel("|point-biserial r|")
    ax.set_title("Numeric vs TARGET (top 15)")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    ax = axes[1]
    y = np.arange(len(cat))
    ax.barh(y, cat.abs_association.values, color=INK, height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels(cat.feature.values, fontsize=7)
    ax.set_xlabel("Cramér's V")
    ax.set_title("Categorical vs TARGET (top 12)")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    fig.subplots_adjust(left=0.24, right=0.98, bottom=0.08, top=0.90, wspace=0.42)
    return savefig(fig, "22_association_screening")


def iv_ranking():
    _, iv, _ = _load_relationship_results()
    top = iv.head(20).sort_values("iv")
    colors = [INK if v >= 0.3 else (GRAY_RAMP[1] if v >= 0.1 else GRAY_RAMP[3])
              for v in top.iv.values]

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 5.4))
    y = np.arange(len(top))
    ax.barh(y, top.iv.values, color=colors, height=0.62)
    for yi, v in zip(y, top.iv.values):
        ax.text(v, yi, f" {v:.3f}", va="center", fontsize=7.5, color=TEXT_SECONDARY)
    ax.set_yticks(y)
    ax.set_yticklabels(top.feature.values, fontsize=7.5)
    ax.set_xlabel("information value (IV)")
    ax.set_title("IV ranking (train fold, top 20)")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    for thr, label in [(0.02, "weak"), (0.1, "medium"), (0.3, "strong")]:
        ax.axvline(thr, color=TEXT_SECONDARY, linewidth=0.6, linestyle=":")
        ax.text(thr, len(top) - 0.4, f" {label}", fontsize=6.5, color=TEXT_SECONDARY,
                va="top", ha="left")
    fig.subplots_adjust(left=0.30, right=0.98, bottom=0.08, top=0.92)
    return savefig(fig, "23_iv_ranking")


def woe_monotonic_examples():
    _, _, woe = _load_relationship_results()
    feats = ["EXT_SOURCE_3", "EXT_SOURCE_2", "EXT_SOURCE_1",
             "DAYS_BIRTH", "DAYS_EMPLOYED", "AMT_CREDIT"]
    xlabels = {
        "EXT_SOURCE_1": "score", "EXT_SOURCE_2": "score", "EXT_SOURCE_3": "score",
        "DAYS_BIRTH": "age (years)", "DAYS_EMPLOYED": "employment (years)",
        "AMT_CREDIT": "credit amount",
    }

    fig, axes = plt.subplots(2, 3, figsize=(DOUBLE_COL, 4.8))
    for ax, feat in zip(axes.flat, feats):
        d = woe[feat]
        bins = [b for b in d["bins"]
                if b["order"] is not None and b["bin"] not in ("Missing", "Other")]
        bins.sort(key=lambda b: b["order"])
        if feat in ("DAYS_BIRTH", "DAYS_EMPLOYED"):
            xs = [-b["order"] / 365.25 for b in bins]
        else:
            xs = [b["order"] for b in bins]
        ys = [b["bad_rate"] * 100 for b in bins]
        ax.plot(xs, ys, color=INK, marker="o", markersize=3, linewidth=1.2)
        ax.axhline(8.07, color=TEXT_SECONDARY, linewidth=0.6, linestyle="--")
        if feat == "DAYS_EMPLOYED":
            miss = next((b for b in d["bins"] if b["bin"] == "Missing"), None)
            if miss is not None:
                ax.text(0.03, 0.05,
                        f"unemployed (sentinel): {miss['bad_rate'] * 100:.1f}%",
                        transform=ax.transAxes, ha="left", va="bottom",
                        fontsize=6.5, color=TEXT_SECONDARY)
        direction = d["direction"] if d["direction"] else ""
        ax.set_title(f"{feat}  (IV {d['iv']:.3f} {direction})", fontsize=8)
        ax.set_xlabel(xlabels[feat], fontsize=7)
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        if feat == "AMT_CREDIT":
            ax.xaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
    for ax in axes[:, 0]:
        ax.set_ylabel("default rate (%)", fontsize=8)
    for ax in axes[:, 1:].flat:
        ax.set_ylabel("")
    fig.subplots_adjust(left=0.08, right=0.99, bottom=0.12, top=0.92,
                        wspace=0.38, hspace=0.55)
    return savefig(fig, "24_woe_monotonic_examples")


def derived_iv_vs_parents():
    derived = pd.read_csv(ROOT / "results/eda/derived_iv_ranking.csv")
    raw = pd.read_csv(ROOT / "results/eda/iv_ranking.csv")
    raw_map = dict(zip(raw["feature"], raw["iv"]))
    parents = {
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
    rows = []
    for _, r in derived.iterrows():
        c = r["feature"]
        best = max(raw_map.get(p, 0.0) for p in parents[c])
        rows.append((c, float(r["iv"]), best))
    rows.sort(key=lambda t: t[1])
    labels = [t[0] for t in rows]
    ratio_iv = [t[1] for t in rows]
    best_iv = [t[2] for t in rows]

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 4.8))
    y = np.arange(len(labels))
    h = 0.34
    ax.barh(y + h / 2, ratio_iv, height=h, color=INK, label="ratio")
    ax.barh(y - h / 2, best_iv, height=h, color=GRAY_RAMP[3], label="best raw parent")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("IV")
    ax.set_title("Derived ratios vs raw parents (train fold)")
    ax.legend(fontsize=7, frameon=False, loc="lower right")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max(best_iv) * 1.25)
    fig.subplots_adjust(left=0.32, right=0.98, bottom=0.08, top=0.92)
    return savefig(fig, "25_derived_iv_vs_parents")


BUILDING_VARS = [
    "APARTMENTS", "BASEMENTAREA", "COMMONAREA", "ELEVATORS", "ENTRANCES",
    "FLOORSMAX", "FLOORSMIN", "LANDAREA", "LIVINGAPARTMENTS", "LIVINGAREA",
    "NONLIVINGAPARTMENTS", "NONLIVINGAREA", "YEARS_BEGINEXPLUATATION", "YEARS_BUILD",
]


def collinearity_heatmap():
    corr = pd.read_csv(ROOT / "results/eda/correlation_matrix.csv", index_col=0)
    order = [f"{v}_{agg}" for v in BUILDING_VARS for agg in ("AVG", "MEDI", "MODE")]
    order = [c for c in order if c in corr.columns]
    sub = corr.loc[order, order]

    fig, ax = plt.subplots(figsize=(DOUBLE_COL, DOUBLE_COL))
    im = ax.imshow(sub.values, cmap="gray_r", vmin=0.0, vmax=1.0, aspect="auto")
    ax.set_xticks(np.arange(len(order)))
    ax.set_yticks(np.arange(len(order)))
    ax.set_xticklabels(order, fontsize=4, rotation=90)
    ax.set_yticklabels(order, fontsize=4)
    ax.set_xticks(np.arange(-0.5, len(order), 3), minor=True)
    ax.set_yticks(np.arange(-0.5, len(order), 3), minor=True)
    ax.grid(which="minor", color="#ffffff", linewidth=1.2)
    ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("Spearman r")
    ax.set_title("Building block: Spearman correlation (train fold)")
    fig.tight_layout(pad=0.4)
    return savefig(fig, "26_collinearity_heatmap")


def importance_iv_crosscheck():
    cross = pd.read_csv(ROOT / "results/eda/importance_iv_crosscheck.csv")
    rho = cross[["importance_mean", "iv"]].corr(method="spearman").iloc[0, 1]
    top_bar = cross.nlargest(15, "importance_mean").sort_values("importance_mean")

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL, 3.6),
                             gridspec_kw={"width_ratios": [1.15, 1]})

    # panel 1 -- scatter of tree importance vs IV
    ax = axes[0]
    strong = cross[cross.iv >= 0.3]
    medium = cross[(cross.iv >= 0.1) & (cross.iv < 0.3)]
    weak = cross[(cross.iv >= 0.02) & (cross.iv < 0.1)]
    none = cross[cross.iv < 0.02]
    ax.scatter(none.iv, none.importance_mean, s=8, color=GRAY_RAMP[4],
               edgecolor="none", label="IV < 0.02")
    ax.scatter(weak.iv, weak.importance_mean, s=10, color=GRAY_RAMP[2],
               edgecolor="none", label="0.02–0.1")
    ax.scatter(medium.iv, medium.importance_mean, s=14, color=GRAY_RAMP[1],
               edgecolor="none", label="0.1–0.3")
    ax.scatter(strong.iv, strong.importance_mean, s=18, color=INK,
               edgecolor="none", label="IV ≥ 0.3")
    ann = ["EXT_SOURCE_3", "EXT_SOURCE_2", "EXT_SOURCE_1", "DAYS_EMPLOYED",
           "DAYS_BIRTH", "AMT_GOODS_PRICE", "ORGANIZATION_TYPE", "AMT_CREDIT"]
    for f in ann:
        r = cross[cross.feature == f].iloc[0]
        ax.annotate(f, (r.iv, r.importance_mean), fontsize=5.5, color=TEXT_SECONDARY,
                    xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel("information value (IV)")
    ax.set_ylabel("permutation importance")
    ax.set_title("Tree importance vs IV")
    ax.text(0.97, 0.03, f"Spearman ρ = {rho:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.5, color=INK)
    ax.legend(fontsize=6, frameon=False, loc="upper left")
    ax.grid(color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    # panel 2 -- top-15 tree importance
    ax = axes[1]
    y = np.arange(len(top_bar))
    ax.barh(y, top_bar.importance_mean.values, color=INK, height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels(top_bar.feature.values, fontsize=7)
    ax.set_xlabel("permutation importance")
    ax.set_title("Top 15 by tree importance")
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    fig.subplots_adjust(left=0.28, right=0.98, bottom=0.10, top=0.90, wspace=0.55)
    return savefig(fig, "27_importance_iv_crosscheck")


def make_all():
    outputs = []
    outputs.append(target_distribution())
    outputs.append(loan_amount_distributions())
    outputs.append(income_distribution())
    outputs.append(days_to_years())
    outputs.append(ext_sources())
    outputs.append(flags_contact_region())
    outputs.append(flags_document())
    outputs.append(bureau_requests())
    outputs.append(social_circle())
    outputs.append(children_family_rating())
    outputs.append(region_population())
    outputs.append(own_car_age())
    outputs.append(categorical_demographic())
    outputs.append(categorical_housing_contract())
    outputs.append(occupation_organization())
    outputs.append(flags_own())
    outputs.append(hour_appr_process())
    outputs.append(sparse_block_missing())
    outputs.append(sparse_block_examples())
    outputs.append(outlier_income())
    outputs.append(outlier_age_ratio())
    outputs.append(outlier_tail_ratio())
    outputs.append(association_screening())
    outputs.append(iv_ranking())
    outputs.append(woe_monotonic_examples())
    outputs.append(derived_iv_vs_parents())
    outputs.append(collinearity_heatmap())
    outputs.append(importance_iv_crosscheck())
    return outputs


if __name__ == "__main__":
    for out in make_all():
        print(out)
