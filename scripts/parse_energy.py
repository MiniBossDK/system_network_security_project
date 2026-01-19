import pandas as pd

def load_energy_data(path):
    df = pd.read_csv(path)

    # Basic sanity checks
    required_cols = {
        "algo", "msg_len", "reps",
        "avg_current_mA", "voltage_V", "energy_uJ"
    }
    if not required_cols.issubset(df.columns):
        raise ValueError("Missing required columns")

    return df

if _name_ == "_main_":
    df = load_energy_data("data/raw/energy_results.csv")
    print(df.head())