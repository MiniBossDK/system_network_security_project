from __future__ import annotations
from pathlib import Path
import pandas as pd
from .config import MEMORY_FILE

def parse_memory() -> pd.DataFrame:
    """
    Expects a CSV like:
    ,ASCON-ENC,ASCON-DEC,AES128-GCM-ENC,...
    RAM (bytes),848,860,1126,...
    Flash (bytes),8182,10180,8376,...
    """
    df = pd.read_csv(MEMORY_FILE, index_col=0)
    # index: "RAM (bytes)" / "Flash (bytes)" ; columns: "ASCON-ENC" etc.

    rows = []
    for col in df.columns:
        # normalize algo/mode
        if "-" not in col:
            continue
        parts = col.split("-")
        mode = parts[-1].lower()  # ENC/DEC
        algo = "-".join(parts[:-1])

        # normalize naming to match power labels
        algo = algo.replace("AES-128-GCM", "AES128-GCM")

        rows.append({
            "algo": algo,
            "mode": "enc" if mode == "enc" else "dec",
            "ram_bytes": int(df.loc["RAM (bytes)", col]),
            "flash_bytes": int(df.loc["Flash (bytes)", col]),
        })

    out = pd.DataFrame(rows).sort_values(["algo", "mode"]).reset_index(drop=True)
    return out
