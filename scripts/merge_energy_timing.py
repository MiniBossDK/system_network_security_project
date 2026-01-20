import pandas as pd
from pathlib import Path

ENERGY = Path("data/processed/energy_results.csv")
TIMING = Path("data/raw/timing_results.csv")
OUT = Path("data/processed/final_results.csv")

def normalize_base(a: str) -> str:
    a = str(a).strip()
    mapping = {
        "AES-GCM": "AES128-GCM",
        "AES128-GCM": "AES128-GCM",
        "AES256-GCM": "AES256-GCM",
        "ASCON": "ASCON128",
        "ASCON128": "ASCON128",
        "ChaChaPoly": "ChaChaPoly",
        "ChaCha20-Poly1305": "ChaChaPoly",
        "CHACHA": "ChaChaPoly",
        "BASELINE": "BASELINE",
    }
    return mapping.get(a, a)

def normalize_full(a: str) -> str:
    a = str(a).strip()
    parts = a.split("-")
    if len(parts) >= 2 and parts[-1] in ("ENC", "DEC", "BASE"):
        base = "-".join(parts[:-1])
        mode = parts[-1]
        return f"{normalize_base(base)}-{mode}"
    return normalize_base(a)

def main():
    dfE = pd.read_csv(ENERGY)
    dfT = pd.read_csv(TIMING)

    # --- Ensure msg_len types are consistent ---
    dfE["msg_len"] = pd.to_numeric(dfE["msg_len"], errors="coerce")
    dfT["msg_len"] = pd.to_numeric(dfT["msg_len"], errors="coerce")

    dfE = dfE.dropna(subset=["msg_len"]).copy()
    dfT = dfT.dropna(subset=["msg_len"]).copy()

    dfE["msg_len"] = dfE["msg_len"].astype(int)
    dfT["msg_len"] = dfT["msg_len"].astype(int)

    # Normalize names
    dfE["algo"] = dfE["algo"].astype(str).str.strip()
    dfT["algo"] = dfT["algo"].apply(normalize_full)

    # --- Baseline current from energy_results.csv ---
    base_rows = dfE[dfE["algo"] == "BASELINE-BASE"]
    if base_rows.empty:
        raise ValueError("Missing BASELINE-BASE in energy_results.csv (baseline current).")
    baseline_current_mA = float(base_rows.iloc[0]["avg_current_mA"])
    baseline_voltage_V = float(base_rows.iloc[0]["voltage_V"])

    # Merge energy + timing on (algo, msg_len)
    df = dfE.merge(
        dfT[["algo", "msg_len", "reps", "avg_us"]],
        on=["algo", "msg_len"],
        how="inner"
    )

    if df.empty:
        print("Merge produced 0 rows.")
        print("Energy algos:", sorted(dfE["algo"].unique().tolist()))
        print("Timing algos:", sorted(dfT["algo"].unique().tolist()))
        return

    # --- Energy computations ---
    df["energy_uJ_raw"] = (df["voltage_V"] * (df["avg_current_mA"] / 1000.0) * (df["avg_us"] * 1e-6)) * 1e6
    df["baseline_uJ"] = (baseline_voltage_V * (baseline_current_mA / 1000.0) * (df["avg_us"] * 1e-6)) * 1e6
    df["energy_uJ_crypto"] = df["energy_uJ_raw"] - df["baseline_uJ"]

    df = df[[
        "algo", "msg_len", "reps", "avg_us",
        "avg_current_mA", "voltage_V",
        "baseline_uJ", "energy_uJ_raw", "energy_uJ_crypto"
    ]].sort_values(["algo", "msg_len"]).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"Wrote {OUT} with {len(df)} rows")
    print(df.head())


if __name__ == "__main__":
    main()
