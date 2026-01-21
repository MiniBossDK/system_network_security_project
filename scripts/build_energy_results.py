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
    "aes256_gcm": "AES256-GCM",
    "ascon": "ASCON128",
    "chacha": "ChaChaPoly",
    "baseline": "BASELINE",  
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
    # baseline files have no msg_len
    if fname.startswith("baseline"):
        return 0

    m = re.search(r"_(\d+)\.csv$", fname)
    if not m:
        raise ValueError(f"Cannot infer msg_len from filename: {fname} (expected enc_16.csv etc)")
    return int(m.group(1))

def infer_mode_from_name(fname: str) -> str:
    if fname.startswith("baseline"):
        return "BASE"
    if fname.startswith("enc_"):
        return "ENC"
    if fname.startswith("dec_"):
        return "DEC"
    raise ValueError(f"Filename must start with enc_ or dec_ or baseline: {fname}")

def compute_avg_current_mA(csv_path: Path, t_min: float = None, t_max: float = None) -> float:
    """
    Average current (mA) from Keithley CSV.

    If t_min/t_max are given, we only average samples whose Relative Time is in [t_min, t_max].
    Relative Time is assumed to be column 14 (0-based index 13) in your export:
    ... Origin,Relative Time,Channel,CH Label
    """
    values_A = []

    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) < 15:
                continue

            unit = parts[1].strip()
            if "Amp" not in unit:
                continue

            # reading in amps
            try:
                val_A = float(parts[0].strip())
            except ValueError:
                continue

            # relative time (seconds)
            # In your export: "... Origin,Relative Time,Channel,CH Label"
            # Relative Time appears near the end and looks like 0.000100000
            try:
                rel_t = float(parts[13].strip())
            except ValueError:
                rel_t = None

            if t_min is not None and rel_t is not None and rel_t < t_min:
                continue
            if t_max is not None and rel_t is not None and rel_t > t_max:
                continue

            if 1e-6 < abs(val_A) < 1.0:
                values_A.append(val_A)

    if not values_A:
        raise ValueError(f"No current readings found in {csv_path} (after time filtering).")

    return float((sum(values_A) / len(values_A)) * 1000.0)


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

            if folder == "baseline":
                # baseline.csv in your example starts at ~10s; take a stable window
                avg_current_mA = compute_avg_current_mA(csv_path, t_min=10.5, t_max=20.0)
            else:
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
