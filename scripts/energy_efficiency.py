import pandas as pd

def calculate_readable_efficiency(input_file, output_file):
    # Load the data
    df = pd.read_csv(input_file)
    
    # 1. Convert Energy to Microjoules (uJ)
    # 1 Joule = 1,000,000 Microjoules
    df['Energy_uJ'] = df['Energy_Joules'] * 1_000_000
    
    # 2. Convert Time to Milliseconds (ms) for readability
    df['Time_ms'] = df['Time_Sec'] * 1000
    
    # 3. Calculate Efficiency in Bits per Microjoule
    # Formula: (Bytes * 8) / Energy_in_uJ
    df['Efficiency_Bits_per_uJ'] = (df['Size_Bytes'] * 8) / df['Energy_uJ']
    
    # Optional: Efficiency in Bytes per Microjoule
    df['Efficiency_Bytes_per_uJ'] = df['Size_Bytes'] / df['Energy_uJ']
    
    # Display the new averages
    summary = df.groupby('Algorithm_File')[['Energy_uJ', 'Efficiency_Bits_per_uJ']].mean()
    summary = summary.rename(columns={'Energy_uJ': 'Avg_Energy (uJ)', 'Efficiency_Bits_per_uJ': 'Efficiency (bits/uJ)'})
    
    print("Average Energy and Efficiency (Rescaled Units):")
    print(summary)
    
    # Save the file
    df.to_csv(output_file, index=False)
    print(f"\nSaved rescaled data to {output_file}")

if __name__ == "__main__":
    calculate_readable_efficiency('final_energy_results.csv', 'energy_efficiency_rescaled.csv')