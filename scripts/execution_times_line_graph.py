import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_with_renamed_algorithms(csv_file):
    # Load the dataset
    df = pd.read_csv(csv_file)

    # Convert Time to Milliseconds (ms)
    df['Time_ms'] = df['Time_Sec'] * 1000

    # Define the Name Mapping
    def get_real_name(filename):
        if 'aes128' in filename:
            return 'AES-128-GCM'
        elif 'aes256' in filename:
            return 'AES-256-GCM'
        elif 'ascon' in filename:
            return 'ASCON128'
        elif 'chacha' in filename:
            return 'ChaCha20-Poly1305'
        else:
            return filename

    # Create a new column for the clean names
    df['Algorithm_Name'] = df['Algorithm_File'].apply(get_real_name)

    # Separate Encryption and Decryption data
    df_enc = df[df['Algorithm_File'].str.contains('_enc')]
    df_dec = df[df['Algorithm_File'].str.contains('_dec')]

    # Helper function to create the plots
    def create_plot(data, title, output_filename):
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")

        # Plot using 'Algorithm_Name' for the legend
        sns.lineplot(
            data=data, 
            x='Size_Bytes', 
            y='Time_ms', 
            hue='Algorithm_Name', 
            marker='o',
            linewidth=2
        )

        # Formatting
        plt.xscale('log', base=2)
        unique_sizes = sorted(data['Size_Bytes'].unique())
        plt.xticks(unique_sizes, unique_sizes)

        plt.title(title, fontsize=14)
        plt.xlabel('Message Size (Bytes)', fontsize=12)
        plt.ylabel('Execution Time (ms)', fontsize=12)
        plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.savefig(output_filename)
        print(f"Saved graph: {output_filename}")

    # Generate the graphs
    create_plot(df_enc, 'Encryption Execution Time vs Message Size', 'encryption_time_plot_renamed.png')
    create_plot(df_dec, 'Decryption Execution Time vs Message Size', 'decryption_time_plot_renamed.png')

if __name__ == "__main__":
    plot_with_renamed_algorithms('final_energy_results.csv')