import pandas as pd
from pathlib import Path

# Paths
RAW_DATA = Path("data/raw/timing_results.csv")
OUT_DATA = Path("data/processed/summary.csv")

# Load CSV
df = pd.read_csv(RAW_DATA)

# Basic sanity check
print("Loaded data:")
print(df.head())

# Sort for readability
df = df.sort_values(by=["algo", "msg_len"])

# Save cleaned version
OUT_DATA.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_DATA, index=False)

print(f"\nProcessed data saved to {OUT_DATA}")
