import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/processed/energy_results.csv")

# Adjust if your supply is different.
VOLTAGE_V = 9.0

# Map folder -> algo name in final table
ALGO_MAP = {
    "aes128_gcm": "AES128-GCM",
    "ascon": "ASCON128",
    "chacha": "ChaChaPoly",
}

# Current column candidates (depends on how Keithley export looks)
CURRENT_COL_CANDIDATES = [
    "current", "Current", "CURRENT",
    "I", "i",
    "Current (A)", "Current(A)",
    "Reading", "reading",
]

def find_current_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c.strip() in CURRENT_COL_CANDIDATES:
            return c
    # fallback: pick first numeric column
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        raise ValueError(f"No numeric columns found. Columns: {df.columns.tolist()}")
    return numeric_cols[0]

def infer_msg_len_from_name(fname: str) -> int:
    m = re.search(r"_(\d+)\.csv$", fname)
    if not m:
        raise ValueError(f"Cannot infer msg_len from filename: {fname} (expected enc_16.csv etc)")
    return int(m.group(1))

def infer_mode_from_name(fname: str) -> str:
    if fname.startswith("enc_"):
        return "ENC"
    if fname.startswith("dec_"):
        return "DEC"
    raise ValueError(f"Filename must start with enc_ or dec_: {fname}")

def compute_avg_current_mA(csv_path: Path) -> float:
    """
    Robust parser for Keithley DMM6500 CSV exports that may contain
    metadata, ragged rows, mixed delimiters, etc.

    Strategy: scan all lines and extract numeric tokens; keep values
    that look like current readings (in A). Then average.
    """

    values_A = []

    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Split on common delimiters (comma, semicolon, tabs)
            parts = re.split(r"[;, \t]+", line)

            for tok in parts:
                # normalize scientific notation like 1.23E-3
                try:
                    v = float(tok)
                except ValueError:
                    continue

                # Heuristic filter: keep values that look like current in Amps.
                # Arduino current is typically 0.02–0.10 A.
                # Accept a wider range just in case.
                if 1e-6 < abs(v) < 1.0:
                    values_A.append(v)

    if not values_A:
        raise ValueError(f"No current-like numeric values found in {csv_path}")

    avg_A = sum(values_A) / len(values_A)
    avg_mA = avg_A * 1000.0
    return float(avg_mA)



def main():
    rows = []

    for folder, algo_name in ALGO_MAP.items():
        algo_dir = RAW_DIR / folder
        if not algo_dir.exists():
            continue

        for csv_path in sorted(algo_dir.glob("*.csv")):
            fname = csv_path.name
            mode = infer_mode_from_name(fname)
            msg_len = infer_msg_len_from_name(fname)

            avg_current_mA = compute_avg_current_mA(csv_path)

            rows.append({
                "algo": f"{algo_name}-{mode}",
                "msg_len": msg_len,
                "avg_current_mA": avg_current_mA,
                "voltage_V": VOLTAGE_V,
                # reps + exec time will be merged later from timing_results
            })

    if not rows:
        raise RuntimeError("No CSVs found. Check folder names and enc_/dec_ filenames.")

    df_energy = pd.DataFrame(rows).sort_values(["algo", "msg_len"]).reset_index(drop=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_energy.to_csv(OUT_PATH, index=False)

    print(f"Wrote {OUT_PATH} with {len(df_energy)} rows")
    print(df_energy.head())

if __name__ == "__main__":
    main()
