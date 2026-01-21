from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from .config import FIG_DIR

def _plot_one(df: pd.DataFrame, mode: str, ycol: str, title: str, ylabel: str, fname: str):
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    d = df[df["mode"] == mode].copy()
    algos = sorted(d["algo"].unique())

    plt.figure(figsize=(10, 6))
    for algo in algos:
        g = d[d["algo"] == algo].sort_values("msg_size")
        x = g["msg_size"].to_numpy()
        y = g[ycol].to_numpy()

        # error bars:
        # - if you have CI across runs, show it; else show within-run std avg (informative, not CI).
        if "CI95_across_runs_mA" in g.columns and g["CI95_across_runs_mA"].notna().any():
            yerr = g["CI95_across_runs_mA"].to_numpy()
        else:
            yerr = g.get("I_std_within_mA_avg", pd.Series([None]*len(g))).to_numpy()

        plt.errorbar(x, y, yerr=yerr, marker="o", capsize=3, label=algo)

    plt.title(title)
    plt.xlabel("Message size (bytes)")
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.legend()
    out = FIG_DIR / fname
    plt.tight_layout()
    plt.savefig(out, dpi=200)
    plt.close()

def plot_all(df_summary: pd.DataFrame):
    _plot_one(
        df_summary, "enc", "I_mean_mA",
        "Mean current vs message size (ENC)",
        "Current (mA)",
        "current_mean_enc.png",
    )
    _plot_one(
        df_summary, "dec", "I_mean_mA",
        "Mean current vs message size (DEC)",
        "Current (mA)",
        "current_mean_dec.png",
    )
    _plot_one(
        df_summary, "enc", "deltaI_mA",
        "Baseline-subtracted current (ΔI) vs size (ENC)",
        "Current (mA)",
        "current_delta_enc.png",
    )
    _plot_one(
        df_summary, "dec", "deltaI_mA",
        "Baseline-subtracted current (ΔI) vs size (DEC)",
        "Current (mA)",
        "current_delta_dec.png",
    )
