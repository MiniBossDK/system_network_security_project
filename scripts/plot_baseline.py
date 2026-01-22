import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASELINE = Path("data/raw/baseline/baseline.csv")
OUT = Path("figures/baseline.png")               
OUT.parent.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(BASELINE, skiprows=9)

    df = df[["Relative Time", "Reading"]]
    df["Reading"] = pd.to_numeric(df["Reading"], errors="coerce")
    df["Relative Time"] = pd.to_numeric(df["Relative Time"], errors="coerce")
    df = df.dropna()


    # Guess the current column name (adapt if yours differs)
    # Common names: "current_mA", "Current (mA)", "reading", "I_mA"
    possible = [c for c in df.columns if "mA" in c or "current" in c.lower() or "reading" in c.lower()]
    if not possible:
        raise ValueError(f"Could not find a current column in {df.columns}")
    col = possible[0]

    y = df[col].astype(float)

    plt.figure()
    plt.plot(y)
    plt.xlabel("Sample index")
    plt.ylabel("Current (mA)")
    plt.title("Reading Plot for baseline.csv")
    plt.tight_layout()
    plt.savefig(OUT, dpi=300)
    print(f"Saved: {OUT}")

if __name__ == "__main__":
    main()
