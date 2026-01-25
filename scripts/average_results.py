import pandas as pd
import argparse
import sys

def calculate_averages(file_path):
    try:
        # Load the dataset
        df = pd.read_csv(file_path)
        
        # 1. Convert Time_Sec to Milliseconds
        df['Time_ms'] = df['Time_Sec'] * 1000
        
        # 2. Parse the 'Algorithm_File' column
        split_data = df['Algorithm_File'].str.rsplit('_', n=1, expand=True)
        df['Algorithm'] = split_data[0]
        df['Variant'] = split_data[1]
        
        # 3. Calculate Stats (Mean for Time; Mean & Std Dev for Energy)
        # We use .agg() to specify different operations for different columns
        grouped = df.groupby(['Algorithm', 'Variant']).agg({
            'Energy_MicroJoules': ['mean', 'std'],
            'Time_ms': 'mean'
        })
        
        # 4. Clean up the Column Names
        # The .agg() function creates a MultiIndex (hierarchical) header. 
        # We flatten it to make it readable (e.g., 'Energy_Mean', 'Energy_Std').
        grouped.columns = [
            'Energy_Mean_uJ', 
            'Energy_Std_uJ', 
            'Time_Mean_ms'
        ]
        
        # Reset index to make Algorithm and Variant normal columns again
        results = grouped.reset_index()
        
        # Display the results
        print("-" * 80)
        print(f"Processed file: {file_path}")
        print("-" * 80)
        # Set float_format to avoid excessive decimal places in display
        print(results.to_string(index=False, float_format="%.4f"))
        print("-" * 80)
        
        # Optional: Save to a new CSV file
        output_filename = "averaged_results_with_std.csv"
        results.to_csv(output_filename, index=False)
        print(f"Results saved to {output_filename}")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Average energy and time from CSV.")
    parser.add_argument("filename", help="The path to the CSV file to process")
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    calculate_averages(args.filename)