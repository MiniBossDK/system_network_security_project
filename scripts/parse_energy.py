import pandas as pd

def load_energy_data(path):
    df = pd.read_csv(path)

    required_cols = {"algo", "msg_len", "avg_current_mA", "voltage_V"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df

def main():
    df = load_energy_data("data/processed/energy_results.csv")
    print(df.head())

if __name__ == "__main__":
    main()
