import os
import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial


def process_file(csv_file, continent, input_directory, output_base_directory, year):
    csv_path = os.path.join(input_directory, csv_file)
    print(f"Processing file: {csv_file} for year: {year}")

    try:
        # Read CSV file into DataFrame
        df = pd.read_csv(csv_path)

        # Filter valid JOIN_FID
        df = df[df['JOIN_FID'] >= 0]

        # Use groupby for aggregation
        bui_column = f'bui_{year}'
        result_df = df.groupby(['JOIN_FID', bui_column], as_index=False)['Area'].sum()

        # Pivot the DataFrame to get the desired format
        result_df = result_df.pivot(index='JOIN_FID', columns=bui_column, values='Area').fillna(0).reset_index()

        # Reset the DataFrame to ensure all building classes are included
        result_df.columns.name = None  # Remove the name of columns
        result_df = result_df.rename(columns={
            'JOIN_FID': 'grid_id',
            'commercial': 'commercial',
            'education': 'education',
            'industrial': 'industrial',
            'medical': 'medical',
            'other': 'other',
            'public': 'public',
            'residential': 'residential'
        })

        # Create output directory (if it does not exist)
        output_directory = os.path.join(output_base_directory, str(year))
        os.makedirs(output_directory, exist_ok=True)

        # Save results to CSV
        output_csv_path = os.path.join(output_directory, f"{os.path.splitext(csv_file)[0]}.csv")
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"Saved results to CSV file: {output_csv_path}")
        return True
    except Exception as e:
        print(f"Error processing file {csv_file}: {e}")
        return False


def main():
    # Define list of continents to loop through
    continents = ["Europe", "Asia", "North America", "Latin America", "Africa", "Oceania"]

    # Set number of processes (adjust based on CPU cores)
    num_processes = cpu_count()

    for continent in continents:
        # Input and output directories
        input_directory = fr"..\{continent}\your spatial join projected csv path"
        output_base_directory = fr"..\{continent}\your built-up area statistics csv path"

        # Get all .csv files
        csv_files = [f for f in os.listdir(input_directory) if f.endswith('.csv')]

        # Create processing function for each year
        for year in range(2017, 2026):
            print(f"\nStarting to process {continent} data for the year {year}...")

            # Use partial to fix some parameters
            process_func = partial(
                process_file,
                continent=continent,
                input_directory=input_directory,
                output_base_directory=output_base_directory,
                year=year
            )

            # Process files in parallel
            with Pool(processes=num_processes) as pool:
                results = pool.map(process_func, csv_files)

            # Print statistics
            success_count = sum(results)
            print(f"{continent} {year}: Successfully processed {success_count}/{len(csv_files)} files")


if __name__ == '__main__':
    main()