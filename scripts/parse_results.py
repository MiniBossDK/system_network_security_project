import pandas as pd
from pathlib import Path

RAW_DATA = Path("data/raw/timing_results.csv")
OUT_DATA = Path("data/processed/summary.csv")


def main():
    df = pd.read_csv(RAW_DATA)

    print("Loaded timing data:")
    print(df.head())

    df = df.sort_values(by=["algo", "msg_len"]).reset_index(drop=True)

    OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DATA, index=False)

    print(f"\nProcessed timing data saved to {OUT_DATA}")


if __name__ == "__main__":
    main()
