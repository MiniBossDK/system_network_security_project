import matplotlib.pyplot as plt
from parse_energy import load_energy_data

def plot_energy(df):
    for algo in df["algo"].unique():
        sub = df[df["algo"] == algo]
        plt.plot(
            sub["msg_len"],
            sub["energy_uJ"],
            marker="o",
            label=algo
        )

    plt.xlabel("Message length (bytes)")
    plt.ylabel("Energy per encryption (µJ)")
    plt.title("Energy consumption: AES-GCM vs ASCON")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if _name_ == "_main_":
    df = load_energy_data("data/processed/energy_results.csv")
    plot_energy(df)