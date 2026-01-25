import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def plot_energy_consumption(csv_file):
    # Load the dataset
    df = pd.read_csv(csv_file)

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
        if data.empty:
            print(f"No data found for {title}")
            return

        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")

        # Plot using 'Algorithm_Name' for the legend
        # We use 'Energy_MicroJoules' for the Y-axis
        sns.lineplot(
            data=data, 
            x='Size_Bytes', 
            y='Energy_MicroJoules', 
            hue='Algorithm_Name', 
            marker='o',
            linewidth=2
        )

        # Log Scale (Base 2) for X-axis
        plt.xscale('log', base=2)
        unique_sizes = sorted(data['Size_Bytes'].unique())
        plt.xticks(unique_sizes, unique_sizes)

        # Labels and Title
        plt.title(title, fontsize=14)
        plt.xlabel('Message Size (Bytes)', fontsize=12)
        plt.ylabel('Energy Consumption (μJ)', fontsize=12)
        plt.legend(title='Algorithm', bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plt.savefig(output_filename)
        print(f"Saved graph: {output_filename}")
        # plt.show() # Uncomment to display on screen

    # Generate the graphs
    create_plot(df_enc, 'Encryption Energy Consumption vs Message Size', 'encryption_energy_plot.png')
    create_plot(df_dec, 'Decryption Energy Consumption vs Message Size', 'decryption_energy_plot.png')

if __name__ == "__main__":
    plot_energy_consumption('final_energy_results.csv')