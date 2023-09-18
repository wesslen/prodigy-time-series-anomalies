import typer
import os
import json
import pandas as pd

app = typer.Typer()

@app.command()
def partition_csv(input_file: str, output_folder: str, partition_window: int):
    """
    Partition a CSV file into non-overlapping sets of rows with a specified window size,
    calculate standard deviation, and save both CSV partition files and a JSONL statistics file.
    """
    try:
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # Load the input CSV file
        df = pd.read_csv(input_file)

        # Calculate the number of partitions needed
        num_partitions = len(df) // partition_window + (len(df) % partition_window > 0)

        # Initialize a list to store statistics for each partition
        partition_statistics = []

        # Partition the data and save as separate CSV files
        for i in range(num_partitions):
            start_idx = i * partition_window
            end_idx = min((i + 1) * partition_window, len(df))

            # Create a new DataFrame for each partition
            partition_df = df.iloc[start_idx:end_idx]

            # Generate the output filename for this partition
            output_file = os.path.join(output_folder, f'partition_{i}.csv')

            # Save the partitioned data to a new CSV file
            partition_df.to_csv(output_file, index=False)

            # Calculate the standard deviation for the 'Price' values
            stdev = partition_df['meter_reading'].std()

            # Create a dictionary for the statistics
            stats = {
                "id": i,
                "file": f'partition_{i}.csv',
                "start": partition_df['timestamp'].iloc[0],
                "end": partition_df['timestamp'].iloc[-1],
                "stdev": stdev
            }

            # Append the statistics to the list
            partition_statistics.append(stats)

        # Generate the JSONL statistics file
        stats_file = os.path.join(output_folder, 'statistics.jsonl')
        with open(stats_file, 'w') as jsonl_file:
            for stats in partition_statistics:
                jsonl_file.write(json.dumps(stats) + '\n')

        typer.echo(f'{num_partitions} CSV files and statistics file created successfully in {output_folder}!')
    except Exception as e:
        typer.echo(f'An error occurred: {str(e)}', err=True)

if __name__ == "__main__":
    app()
