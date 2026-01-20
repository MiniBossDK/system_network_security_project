import pandas as pd
import matplotlib.pyplot as plt

def main():
    df = pd.read_csv("data/processed/final_results.csv")

    for algo in df["algo"].unique():
        sub = df[df["algo"] == algo]
        plt.plot(sub["msg_len"], sub["energy_uJ"], marker="o", label=algo)

    plt.xlabel("Message length (bytes)")
    plt.ylabel("Energy per operation (µJ)")
    plt.title("Energy vs message size")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
