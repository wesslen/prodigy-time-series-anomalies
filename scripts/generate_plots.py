import typer
import os
import srsly
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
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
        stats_records = list(srsly.read_jsonl(input_jsonl))

        # Load all CSV files and combine them for the overall plot
        all_data = pd.DataFrame()
        for record in stats_records:
            file_name = record['file']
            csv_file_path = os.path.join(input_files, file_name)
            df = pd.read_csv(csv_file_path)
            all_data = pd.concat([all_data, df])

        # Filter records based on the threshold
        filtered_records = [record for record in stats_records if record['stdev'] > threshold or record['stdev'] < 1]

        # Convert the 'timestamp' column to a timestamptime type
        all_data['timestamp'] = pd.to_datetime(all_data['timestamp'])

        # Generate and save individual plots for filtered records with formatted x-axis labels
        for i, record in enumerate(filtered_records):
            file_name = record['file']
            csv_file_path = os.path.join(input_files, file_name)
            df = pd.read_csv(csv_file_path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            first_record_date = df['timestamp'].iloc[0]
            month_year_string = first_record_date.strftime('%Y-%m')

            plt.figure(figsize=(10, 6))
            
            # Plot the individual filtered record
            plt.subplot(211)
            plt.plot(df['timestamp'], df['meter_reading'])

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Set the interval as needed

            plt.xlabel('timestamp')
            plt.ylabel('meter_reading')
            plt.title(f'Plot for Day {i}')
            
            # Format x-axis labels to show only five labels
            ax = plt.gca()
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=5))

            # Plot the overall time series
            plt.subplot(212)
            month_data = all_data[all_data['timestamp'].dt.strftime('%Y-%m') == month_year_string]
            plt.plot(month_data['timestamp'], month_data['meter_reading'], color='blue')

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))  # Set the interval as needed

            plt.xlabel('timestamp')
            plt.ylabel('meter_reading')
            plt.title(f'Temperature Plot for {month_year_string}')
            plt.fill_between(month_data['timestamp'], month_data['meter_reading'].min(), month_data['meter_reading'].max(), where=(month_data['timestamp']>record['start']) & (month_data['timestamp']<=record['end']), alpha=0.2, color='blue', label='Shading')
            
            ax = plt.gca()
            ax.xaxis.set_major_locator(ticker.MaxNLocator(nbins=12))

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
