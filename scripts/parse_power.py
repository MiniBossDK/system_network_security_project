from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import numpy as np
import pandas as pd

from .config import DATA_RAW, ALGO_FOLDERS, BASELINE_FILE, TRIM_FRACTION
from .keithley_csv import read_keithley_current_mA

SIZE_RE = re.compile(r"_(\d+)\.csv$", re.IGNORECASE)

def trimmed_mean(x: np.ndarray, frac: float) -> float:
    if frac <= 0:
        return float(np.mean(x))
    n = len(x)
    k = int(n * frac)
    if 2 * k >= n:
        return float(np.mean(x))
    xs = np.sort(x)
    return float(np.mean(xs[k:-k]))

@dataclass
class BaselineStats:
    mean_mA: float
    std_mA: float
    n: int

def compute_baseline() -> BaselineStats:
    x = read_keithley_current_mA(BASELINE_FILE)
    return BaselineStats(mean_mA=float(np.mean(x)), std_mA=float(np.std(x, ddof=1)), n=len(x))

def parse_power() -> tuple[pd.DataFrame, pd.DataFrame, BaselineStats]:
    """
    Returns:
      df_by_file: one row per CSV file
      df_summary: one row per (algo,mode,msg_size)
      baseline_stats
    """
    baseline = compute_baseline()
    rows = []

    for folder, algo_label in ALGO_FOLDERS.items():
        algo_dir = DATA_RAW / folder
        if not algo_dir.exists():
            continue

        for csv_path in sorted(algo_dir.glob("*.csv")):
            name = csv_path.name.lower()
            if not (name.startswith("enc_") or name.startswith("dec_")):
                continue

            mode = "enc" if name.startswith("enc_") else "dec"
            m = SIZE_RE.search(csv_path.name)
            if not m:
                continue
            msg_size = int(m.group(1))

            x = read_keithley_current_mA(csv_path)
            mean = trimmed_mean(x, TRIM_FRACTION)
            std = float(np.std(x, ddof=1))

            rows.append({
                "algo": algo_label,
                "mode": mode,
                "msg_size": msg_size,
                "file": str(csv_path),
                "I_mean_mA": mean,
                "I_std_mA": std,
                "N_samples": int(len(x)),
            })

    df_by_file = pd.DataFrame(rows).sort_values(["algo", "mode", "msg_size"]).reset_index(drop=True)

    # Summary over runs: if multiple files exist per condition, compute across-run std/CI.
    grouped = df_by_file.groupby(["algo", "mode", "msg_size"], as_index=False)
    out = []
    for (algo, mode, msg_size), g in grouped:
        means = g["I_mean_mA"].to_numpy()
        within_std_avg = float(g["I_std_mA"].mean())

        n_runs = len(g)
        if n_runs >= 2:
            std_across = float(np.std(means, ddof=1))
            ci95 = 1.96 * std_across / np.sqrt(n_runs)
        else:
            std_across = np.nan
            ci95 = np.nan

        out.append({
            "algo": algo,
            "mode": mode,
            "msg_size": int(msg_size),
            "I_mean_mA": float(means.mean()),
            "I_std_within_mA_avg": within_std_avg,
            "I_std_across_runs_mA": std_across,
            "CI95_across_runs_mA": ci95,
            "N_runs": n_runs,
            "baseline_mean_mA": baseline.mean_mA,
            "deltaI_mA": float(means.mean() - baseline.mean_mA),
        })

    df_summary = pd.DataFrame(out).sort_values(["mode", "algo", "msg_size"]).reset_index(drop=True)
    return df_by_file, df_summary, baseline
