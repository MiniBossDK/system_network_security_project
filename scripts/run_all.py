from __future__ import annotations
from pathlib import Path

from .config import DATA_PROCESSED
from .parse_power import parse_power
from .parse_memory import parse_memory
from .merge_results import merge_results
from .plot_results import plot_all

def main():
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

    df_by_file, df_power_summary, baseline = parse_power()
    df_memory = parse_memory()
    df_final = merge_results(df_power_summary, df_memory)

    (DATA_PROCESSED / "current_by_file.csv").write_text(df_by_file.to_csv(index=False), encoding="utf-8")
    (DATA_PROCESSED / "current_summary.csv").write_text(df_power_summary.to_csv(index=False), encoding="utf-8")
    (DATA_PROCESSED / "memory_results.csv").write_text(df_memory.to_csv(index=False), encoding="utf-8")
    (DATA_PROCESSED / "final_results.csv").write_text(df_final.to_csv(index=False), encoding="utf-8")

    meta = []
    meta.append("Power/Current processing metadata\n")
    meta.append(f"Baseline file: {baseline}\n")
    meta.append(f"Baseline mean (mA): {baseline.mean_mA:.6f}\n")
    meta.append(f"Baseline std  (mA): {baseline.std_mA:.6f}\n")
    meta.append(f"Baseline samples: {baseline.n}\n\n")
    meta.append("Note: CI is computed across repeat runs *only if multiple files exist per (algo,mode,size).* \n")
    meta.append("If only one file exists, CI is left blank (NaN).\n")
    (DATA_PROCESSED / "run_metadata.txt").write_text("".join(meta), encoding="utf-8")

    plot_all(df_power_summary)

if __name__ == "__main__":
    main()
