from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
FIG_DIR = ROOT / "figures"

BASELINE_FILE = DATA_RAW / "baseline" / "baseline.csv"
MEMORY_FILE = DATA_RAW / "memory_consumption.csv"

# Folder name -> algorithm label used in plots/paper
ALGO_FOLDERS = {
    "ascon": "ASCON",
    "chacha": "ChaCha20-Poly1305",
    "aes128_gcm": "AES128-GCM",
    "aes256_gcm": "AES256-GCM",
}

# Expected message sizes (bytes)
MSG_SIZES = [16, 32, 64, 128, 256, 512]

# If you want a bit more robustness against spikes:
TRIM_FRACTION = 0.0  # set to 0.01 for 1% trimmed mean (optional)
