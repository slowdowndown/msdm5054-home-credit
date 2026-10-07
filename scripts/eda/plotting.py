"""Plotting style and helpers for Home Credit EDA and report figures.

Single style entry point. Every figure imports this module and calls
set_style() once, so the whole report reads as one system. The style is a
clean black-and-white academic look (serif type, hairline axes, grayscale
marks, no chartjunk).
"""
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")  # figures are saved to disk, not shown interactively
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# --- Ink / surface (black-and-white) --------------------------------------
INK = "#111111"          # primary text and the emphasized (positive) class
PAPER = "#ffffff"        # surface
TEXT_PRIMARY = "#111111"
TEXT_SECONDARY = "#555555"
GRID = "#e3e3e3"         # hairline grid, one shade off surface

# Fixed ordered grayscale series. Identity comes from luminance plus direct
# labels/line style; never cycled past this list. Beyond 5 series, facet or
# fold the tail into "Other".
GRAY_RAMP = ["#111111", "#555555", "#888888", "#b0b0b0", "#d9d9d9"]

# --- Figure sizing (NIPS column widths, inches) -----------------------------
SINGLE_COL = 3.5
DOUBLE_COL = 7.0
GOLDEN = 0.618


def grayscale(n):
    """Return n grayscale colors in fixed order (clamped to the ramp length)."""
    if n <= 0:
        return []
    return GRAY_RAMP[:n]


def set_style():
    plt.rcParams.update({
        # output
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        # type
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif", "Liberation Serif"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.titlelocation": "center",
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        # axes: hairline, out-facing ticks, only left + bottom spines
        "axes.linewidth": 0.8,
        "axes.edgecolor": TEXT_PRIMARY,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "axes.axisbelow": True,
        "axes.unicode_minus": False,
        # grid: solid hairline, recessive
        "axes.grid": False,
        "grid.linewidth": 0.6,
        "grid.color": GRID,
        "grid.alpha": 1.0,
        # lines: rounded, thin
        "lines.linewidth": 1.5,
        "lines.solid_capstyle": "round",
        "lines.solid_joinstyle": "round",
        # bars: no border around marks
        "patch.linewidth": 0.0,
        # legend: no box
        "legend.frameon": False,
        "legend.borderpad": 0.2,
        "legend.handlelength": 1.2,
        "legend.handletextpad": 0.5,
    })


def new_figure(width=SINGLE_COL, height=None):
    """Create a figure at NIPS column width (golden-ratio height by default)."""
    if height is None:
        height = width * GOLDEN
    fig, ax = plt.subplots(figsize=(width, height))
    return fig, ax


def savefig(fig, name, out_dir="results/eda/figures"):
    """Save a figure as PNG, then close it."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    png = out / f"{name}.png"
    fig.savefig(png, dpi=150)
    plt.close(fig)
    return png


def compact_k(x, _pos=None):
    """Tick formatter: 250000 -> '250k', 1200000 -> '1.2M'."""
    if abs(x) >= 1e6:
        return f"{x / 1e6:.1f}M"
    if abs(x) >= 1e3:
        return f"{x / 1e3:.0f}k"
    return f"{x:.0f}"


def bar_count(ax, categories, values, colors=None, width=0.55, fmt="{:,}"):
    """Draw thin capped bars with values labelled at the tips. Returns bars."""
    colors = colors or grayscale(len(categories))
    bars = ax.bar(categories, values, color=colors, width=width)
    for b, v in zip(bars, values):
        ax.annotate(
            fmt.format(v),
            (b.get_x() + b.get_width() / 2, b.get_height()),
            ha="center", va="bottom", xytext=(0, 3), textcoords="offset points",
            fontsize=9, color=TEXT_PRIMARY,
        )
    return bars


def histogram(ax, x, logx=False, nbins=40, color=INK):
    """Draw a single-series histogram. With logx=True, use log-spaced bins on
    positive values and a log x-axis (for heavy right skew such as amounts)."""
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if logx:
        x = x[x > 0]
        bins = np.logspace(np.log10(x.min()), np.log10(x.max()), nbins)
        ax.set_xscale("log")
    else:
        bins = nbins
    ax.hist(x, bins=bins, color=color)
    ax.margins(x=0)
    return ax


def _pct_label(x):
    """Format a 0-100 percentage with precision suited to its magnitude."""
    if x >= 10:
        return f"{x:.0f}%"
    if x >= 1:
        return f"{x:.1f}%"
    if x >= 0.01:
        return f"{x:.2f}%"
    return f"{x:.4f}%"


def hbar_proportion(ax, labels, props, xlabel="% = 1"):
    """Horizontal bars of proportions (0-1) with percentage labels, sorted
    ascending. For binary flags and Y/N ownership columns: the number is the
    chart, so each bar shows the share of the positive value."""
    pairs = sorted(zip(labels, props), key=lambda t: t[1])
    labels = [p[0] for p in pairs]
    props100 = [p[1] * 100 for p in pairs]
    y = np.arange(len(labels))
    ax.barh(y, props100, color=INK, height=0.6)
    for yi, p in zip(y, props100):
        ax.text(p + 0.6, yi, _pct_label(p), va="center", fontsize=8,
                color=TEXT_SECONDARY)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 104)
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8)
    return ax


def hbar_topn(ax, series, topn=10, dropna=True):
    """Horizontal bars of the top-N category counts, tail folded into 'Other'.
    For categorical features with long level names."""
    s = series.dropna() if dropna else series
    vc = s.value_counts()
    top = vc.head(topn)
    if len(vc) > topn:
        other = vc.iloc[topn:].sum()
        labels = list(top.index) + ["Other"]
        vals = list(top.values) + [other]
    else:
        labels = list(top.index)
        vals = list(top.values)
    y = np.arange(len(labels))
    ax.barh(y, vals, color=INK, height=0.6)
    for yi, v in zip(y, vals):
        ax.text(v, yi, compact_k(v), va="center", ha="left", fontsize=8,
                color=TEXT_SECONDARY)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8)
    ax.set_xlabel("Count")
    return ax


def count_bars(ax, series, cap=15, dropna=True):
    """Vertical bars of integer count frequencies, tail folded into 'cap+'.
    For low-cardinality counts and ordinal ratings."""
    s = series.dropna() if dropna else series
    vc = s.value_counts().sort_index()
    idx = [int(i) for i in vc.index]
    vals = list(vc.values)
    if len(idx) > cap:
        labels = [str(i) for i in idx[:cap - 1]] + [f"{cap - 1}+"]
        bars = vals[:cap - 1] + [sum(vals[cap - 1:])]
    else:
        labels = [str(i) for i in idx]
        bars = vals
    ax.bar(labels, bars, color=INK, width=0.7)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(compact_k))
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=8)
    return ax
