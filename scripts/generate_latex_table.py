import pandas as pd
import sys
import os

INPUT_FILE = "final_energy_results.csv"

def format_algo_name(name):
    """
    Converts raw filenames into readable LaTeX-friendly names.
    Example: 'aes128_enc' -> 'AES128 Enc'
    """
    # specific replacements
    replacements = {
        "aes": "AES",
        "cha": "ChaCha",
        "sha": "SHA",
        "enc": "Enc",
        "dec": "Dec",
        "sign": "Sign",
        "verify": "Verify",
        "hash": "Hash"
    }
    
    parts = name.split('_')
    new_parts = []
    
    for p in parts:
        # Check if part contains digits (e.g. aes128)
        head = p.rstrip('0123456789')
        tail = p[len(head):]
        
        # Capitalize or replace known acronyms
        if head.lower() in replacements:
            head = replacements[head.lower()]
        else:
            head = head.capitalize()
            
        new_parts.append(head + tail)
        
    return " ".join(new_parts)

def generate_latex():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found. Run the analysis script first.")
        return

    df = pd.read_csv(INPUT_FILE)

    # 1. Filter and Order Columns
    # We select the specific columns requested
    cols_to_keep = [
        "Algorithm_File", 
        "Sample_Count", 
        "Total_Current_Mean_A", 
        "Total_Current_SD_A", 
        "CI_95_Margin_A", 
        "CI_Lower_Bound_A", 
        "CI_Upper_Bound_A"
    ]
    
    # Check if columns exist
    missing = [c for c in cols_to_keep if c not in df.columns]
    if missing:
        print(f"Error: Missing columns in CSV: {missing}")
        return

    df = df[cols_to_keep].copy()

    # 2. Format Data
    # Clean Algorithm Names
    df["Algorithm_File"] = df["Algorithm_File"].apply(format_algo_name)
    
    # Format Numbers (Scientific notation or fixed point based on magnitude)
    # We generally want readable Amps (e.g., 0.0453)
    pd.options.display.float_format = '{:.6f}'.format

    # 3. Rename Columns for Compact LaTeX
    # Maps internal CSV headers to short LaTeX headers
    header_map = {
        "Algorithm_File": "Algorithm",
        "Sample_Count": "$N$",
        "Total_Current_Mean_A": "$\\bar{I}$ (A)",     # Mean Current
        "Total_Current_SD_A": "$\\sigma_I$ (A)",      # Standard Deviation
        "CI_95_Margin_A": "Margin ($\\pm$)",          # Margin of error
        "CI_Lower_Bound_A": "CI Low",
        "CI_Upper_Bound_A": "CI High"
    }
    
    df.rename(columns=header_map, inplace=True)

    # 4. Generate LaTeX
    # 'index=False' removes the pandas row numbers
    # 'float_format' controls precision in the latex output
    latex_code = df.to_latex(
        index=False,
        escape=False, # Allow $ symbols in headers
        float_format="%.5f", # 5 decimal places for precision
        column_format="l c c c c c c", # Alignments: left, center...
        caption="Current Measurement Statistics with 95\% Confidence Intervals",
        label="tab:power_stats"
    )

    # 5. Wrap in resizebox for compactness
    print("% Copy the following block into your LaTeX document:")
    print("-" * 50)
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\resizebox{\\textwidth}{!}{%")
    print(latex_code.strip())
    print("}")
    print("\\end{table}")
    print("-" * 50)

if __name__ == "__main__":
    generate_latex()