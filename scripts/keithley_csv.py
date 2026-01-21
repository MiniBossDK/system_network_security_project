from __future__ import annotations
from pathlib import Path
import csv
import numpy as np

def _find_data_header_line(lines: list[str]) -> int:
    """
    Returns the index of the line that starts with:
    Reading,Unit,Range Digits,...
    """
    for i, line in enumerate(lines):
        if line.strip().startswith("Reading,Unit"):
            return i
    raise ValueError("Could not find Keithley data header line starting with 'Reading,Unit'")

def read_keithley_current_mA(path: Path) -> np.ndarray:
    """
    Returns an array of current samples in mA from a Keithley CSV export.
    Assumes first column after header is the numeric Reading in Amps.
    """
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    header_idx = _find_data_header_line(text)

    # Data begins on next line
    data_lines = text[header_idx + 1 :]
    reader = csv.reader(data_lines)

    samples_A = []
    for row in reader:
        if not row:
            continue
        # First column is Reading (Amps)
        try:
            samples_A.append(float(row[0]))
        except ValueError:
            # Skip any non-numeric lines
            continue

    arr_A = np.asarray(samples_A, dtype=float)
    return arr_A * 1e3  # mA
