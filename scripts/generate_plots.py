import typer
import os
import srsly
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd

app = typer.Typer()

@app.command()
def generate_plots(
    input_jsonl: str,
    threshold: float,
    input_files: str,
    output_images: str
):
    """
    Generate JPG images of plots for CSV files based on a threshold from a JSONL statistics file.
    """
    try:
        # Create the output images folder if it doesn't exist
        os.makedirs(output_images, exist_ok=True)

        # Read the JSONL statistics file
        stats_records = srsly.read_jsonl(input_jsonl)

        # Filter records based on the threshold
        filtered_records = [record for record in stats_records if record['stdev'] > threshold]

        # Load all CSV files and combine them for the overall plot
        all_data = pd.DataFrame()
        for record in filtered_records:
            file_name = record['file']
            csv_file_path = os.path.join(input_files, file_name)
            df = pd.read_csv(csv_file_path)
            all_data = pd.concat([all_data, df])

        # Convert the 'Date' column to a datetime type
        all_data['Date'] = pd.to_datetime(all_data['Date'])

        # Generate and save individual plots for filtered records with formatted x-axis labels
        for i, record in enumerate(filtered_records):
            file_name = record['file']
            csv_file_path = os.path.join(input_files, file_name)
            df = pd.read_csv(csv_file_path)

            plt.figure(figsize=(10, 6))
            
            # Plot the individual filtered record
            plt.subplot(211)
            plt.plot(df['Date'], df['Price'])
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(f'Plot for {file_name}')
            
            # Format x-axis labels to show only five labels
            ax = plt.gca()
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

            # Plot the overall time series
            plt.subplot(212)
            plt.plot(all_data['Date'], all_data['Price'], color='blue')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title('Overall Time Series Plot')
            plt.fill_between(all_data['Date'], all_data['Price'].min(), all_data['Price'].max(), where=(all_data['Date']>record['start']) & (all_data['Date']<=record['end']), alpha=0.2, color='blue', label='Shading')
            
            plt.tight_layout()
            
            # Save the combined plot with subplots as a JPG file
            output_file_path = os.path.join(output_images, f'combined_plot_{file_name}.jpg')
            plt.savefig(output_file_path)
            plt.close()

        typer.echo(f'Combined plots saved in {output_images}')
    except Exception as e:
        typer.echo(f'An error occurred: {str(e)}', err=True)

if __name__ == "__main__":
    app()
