from __future__ import annotations
import pandas as pd

def merge_results(df_power_summary: pd.DataFrame, df_memory: pd.DataFrame) -> pd.DataFrame:
    df = df_power_summary.merge(df_memory, on=["algo", "mode"], how="left")
    return df
