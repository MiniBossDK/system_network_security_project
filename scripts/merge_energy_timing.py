import pandas as pd
from pathlib import Path

ENERGY = Path("data/processed/energy_results.csv")
TIMING = Path("data/raw/timing_results.csv")
OUT = Path("data/processed/final_results.csv")

def normalize_base(a: str) -> str:
    a = a.strip()
    mapping = {
        "AES-GCM": "AES128-GCM",
        "AES128-GCM": "AES128-GCM",
        "ASCON": "ASCON128",
        "ASCON128": "ASCON128",
        "ChaChaPoly": "ChaChaPoly",
        "ChaCha20-Poly1305": "ChaChaPoly",
        "CHACHA": "ChaChaPoly",
    }
    return mapping.get(a, a)

def main():
    dfE = pd.read_csv(ENERGY)
    dfT = pd.read_csv(TIMING)

    # timing must have these columns
    for c in ["algo", "msg_len", "reps", "avg_us"]:
        if c not in dfT.columns:
            raise ValueError(f"timing_results.csv missing column: {c}")

    # If timing already has ENC/DEC, just normalize and merge
    has_mode = dfT["algo"].astype(str).str.endswith(("ENC", "DEC")).any()

    if has_mode:
        # normalize full algo name
        def norm_full(a: str) -> str:
            a = a.strip()
            parts = a.split("-")
            if len(parts) >= 2 and parts[-1] in ("ENC", "DEC"):
                base = "-".join(parts[:-1])
                mode = parts[-1]
                return f"{normalize_base(base)}-{mode}"
            return normalize_base(a)

        dfT["algo"] = dfT["algo"].astype(str).apply(norm_full)

    else:
        # timing has only base algos (AES-GCM, ASCON, ...)
        # duplicate into ENC and DEC so it can match energy algos
        dfT["algo"] = dfT["algo"].astype(str).apply(normalize_base)

        df_enc = dfT.copy()
        df_enc["algo"] = df_enc["algo"] + "-ENC"

        df_dec = dfT.copy()
        df_dec["algo"] = df_dec["algo"] + "-DEC"

        dfT = pd.concat([df_enc, df_dec], ignore_index=True)

    # merge
    df = dfE.merge(dfT[["algo", "msg_len", "reps", "avg_us"]], on=["algo", "msg_len"], how="inner")

    if df.empty:
        print("Merge produced 0 rows. Still mismatch.")
        print("Energy algos:", sorted(dfE["algo"].unique().tolist()))
        print("Timing algos:", sorted(dfT["algo"].unique().tolist()))
        return

    # energy per op (uJ): V * I(A) * t(s) -> J, then *1e6
    df["energy_uJ"] = (df["voltage_V"] * (df["avg_current_mA"] / 1000.0) * (df["avg_us"] * 1e-6)) * 1e6

    df = df[["algo", "msg_len", "reps", "avg_us", "avg_current_mA", "voltage_V", "energy_uJ"]]
    df = df.sort_values(["algo", "msg_len"]).reset_index(drop=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"Wrote {OUT} with {len(df)} rows")
    print(df.head())

if __name__ == "__main__":
    main()
