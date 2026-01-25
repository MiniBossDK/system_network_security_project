import pandas as pd
import numpy as np
import os
import glob
import sys

# --- CONFIGURATION ---
VOLTAGE = 5.0          # Voltage of the board (5.0V for Uno, 3.3V for others)
BASELINE_FILE = "base.csv"
CONFIDENCE_LEVEL_Z = 1.96 # Z-score for 95% confidence (approximate for large N)

def get_baseline_current(file_path):
    """Calculates the average idle current from base.csv"""
    if not os.path.exists(file_path):
        print(f"[WARNING] Baseline file '{file_path}' not found. Assuming 0A baseline (not recommended).")
        return 0.0
    
    try:
        header_row = 0
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith("Reading,Unit"):
                    header_row = i
                    break
        
        df = pd.read_csv(file_path, skiprows=header_row)
        df['Reading'] = pd.to_numeric(df['Reading'], errors='coerce')
        return df['Reading'].mean()
    except Exception as e:
        print(f"[ERROR] Could not process baseline file: {e}")
        sys.exit(1)

def load_timing_data():
    """
    Scans for timing files (e.g., aes256_enc.csv) and builds a lookup dictionary.
    Returns: dict key=(filename_base, size) -> time_in_seconds
    """
    timing_map = {}
    all_csvs = glob.glob("*.csv")
    timing_files = [f for f in all_csvs if not f[0].isdigit() and "summary" not in f and f != BASELINE_FILE]
    
    print(f"--- Loading Timing Data ---")
    for csv_file in timing_files:
        name_no_ext = os.path.splitext(csv_file)[0]
        if name_no_ext.split('_')[-1].isdigit():
            continue

        try:
            df = pd.read_csv(csv_file)
            df.columns = [c.strip() for c in df.columns]
            
            if 'msg_len' not in df.columns or 'avg_us' not in df.columns:
                continue 
            
            print(f"  Loaded timings from: {csv_file}")
            
            for _, row in df.iterrows():
                size = int(row['msg_len'])
                time_s = float(row['avg_us']) / 1_000_000.0 
                timing_map[(name_no_ext, size)] = time_s
                
        except Exception:
            continue
            
    return timing_map

def analyze_power_file(file_path):
    """
    Calculates mean, standard deviation, and count of the RAW current readings.
    Returns: (mean_amps, std_amps, sample_count)
    """
    try:
        header_row = 0
        with open(file_path, 'r') as f:
            for i, line in enumerate(f):
                if line.startswith("Reading,Unit"):
                    header_row = i
                    break
        
        df = pd.read_csv(file_path, skiprows=header_row)
        df['Reading'] = pd.to_numeric(df['Reading'], errors='coerce')
        
        # Calculate statistics
        mean_val = df['Reading'].mean()
        std_val = df['Reading'].std()
        count_val = df['Reading'].count()
        
        if pd.isna(std_val):
            std_val = 0.0
            
        return mean_val, std_val, count_val
    except:
        return None, None, 0

def main():
    print("=== Cryptographic Power & Energy Analysis ===")
    
    # 1. Get Baseline
    baseline_amps = get_baseline_current(BASELINE_FILE)
    print(f"Baseline Current (Idle): {baseline_amps:.6f} A")
    print("-" * 40)

    # 2. Load Timings
    timing_db = load_timing_data()
    
    # 3. Process Power Files
    results = []
    power_files = glob.glob("*.csv")
    
    print("-" * 40)
    print("Processing Measurement Files...")
    
    for p_file in power_files:
        base_name = os.path.splitext(p_file)[0]
        parts = base_name.split('_')
        
        if len(parts) < 3 or not parts[-1].isdigit():
            continue
            
        algo_op_name = "_".join(parts[:-1]) 
        size = int(parts[-1])              
        
        # A. Get Measured Stats
        measured_amps, measured_std, sample_count = analyze_power_file(p_file)
        if measured_amps is None or sample_count == 0:
            continue
            
        # B. Get Execution Time
        exec_time = timing_db.get((algo_op_name, size))
        
        if exec_time is None:
            print(f"  [SKIP] {p_file}: No matching timing data found")
            continue
            
        # C. Calculate Metrics
        net_current = measured_amps - baseline_amps
        
        # 95% Confidence Interval Calculation
        # CI = Mean +/- (Z * (std / sqrt(N)))
        standard_error = measured_std / np.sqrt(sample_count)
        ci_margin = CONFIDENCE_LEVEL_Z * standard_error
        
        # Power & Energy
        avg_power_watts = net_current * VOLTAGE
        energy_joules = avg_power_watts * exec_time
        
        results.append({
            "Algorithm_File": algo_op_name,
            "Size_Bytes": size,
            "Sample_Count": sample_count,
            "Time_Sec": exec_time,
            
            # Current Stats
            "Total_Current_Mean_A": measured_amps,
            "Total_Current_SD_A": measured_std,
            "CI_95_Margin_A": ci_margin,
            "CI_Lower_Bound_A": measured_amps - ci_margin,
            "CI_Upper_Bound_A": measured_amps + ci_margin,
            
            # Final Energy
            "Energy_MicroJoules": energy_joules * 1_000_000
        })
        
        # Display with CI
        print(f"  [OK] {p_file} (N={sample_count}) -> Current: {measured_amps:.5f} +/- {ci_margin:.5f} A")

    # 4. Save Summary
    if results:
        df_res = pd.DataFrame(results)
        df_res.sort_values(by=["Algorithm_File", "Size_Bytes"], inplace=True)
        
        out_file = "final_energy_results.csv"
        df_res.to_csv(out_file, index=False)
        print("=" * 40)
        print(f"Successfully saved combined analysis to {out_file}")
        print("=" * 40)
        
        # Preview relevant columns
        cols = ["Algorithm_File", "Size_Bytes", "Sample_Count", "Total_Current_SD_A", "CI_95_Margin_A", "Energy_MicroJoules"]
        print(df_res[cols].to_string(index=False))
    else:
        print("\nNo matching data pairs found. Check your filenames.")

if __name__ == "__main__":
    main()