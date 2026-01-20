import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA = Path("data/processed/summary.csv")
OUT = Path("images/time_vs_size.png")


def main():
    df = pd.read_csv(DATA)

    plt.figure(figsize=(6, 4))

    for algo in df["algo"].unique():
        sub = df[df["algo"] == algo]
        plt.plot(sub["msg_len"], sub["avg_us"], marker="o", label=algo)

    plt.xlabel("Message size (bytes)")
    plt.ylabel("Average time per operation (µs)")
    plt.title("Execution time vs message size")
    plt.legend()
    plt.grid(True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"Plot saved to {OUT}")


if __name__ == "__main__":
    main()
