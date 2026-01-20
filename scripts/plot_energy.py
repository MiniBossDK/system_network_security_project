import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path("images/energy_vs_size.png")

def main():
    df = pd.read_csv("data/processed/final_results.csv")

    plt.figure(figsize=(6, 4))

    for algo in df["algo"].unique():
        sub = df[df["algo"] == algo].sort_values("msg_len")
        # Plot RAW energy (no baseline subtraction)
        plt.plot(sub["msg_len"], sub["energy_uJ_raw"], marker="o", label=algo)

    plt.xlabel("Message length (bytes)")
    plt.ylabel("Energy per operation (µJ)")
    plt.title("RAW energy vs message size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot saved to {OUT}")

if __name__ == "__main__":
    main()
