import pandas as pd
import numpy as np
import os
from multiprocessing import Pool
import functools


# Function to calculate three types of Hill numbers
def calculate_hill_numbers(proportions):
    hill_number_0 = np.sum(proportions > 0)
    if hill_number_0 == 0:
        return hill_number_0, 0, 0

    hill_number_1 = np.exp(-np.sum(proportions * np.log(proportions)))
    hill_number_2 = 1 / np.sum(proportions ** 2)
    return hill_number_0, hill_number_1, hill_number_2


def process_file(continent, year, base_input_directory, base_output_directory, file_name):
    input_directory = os.path.join(base_input_directory, str(year))
    output_directory = os.path.join(base_output_directory, str(year))

    file_path = os.path.join(input_directory, file_name)
    try:
        df_area = pd.read_csv(file_path)
        # Remove the column named 'other'
        if 'other' in df_area.columns:
            df_area = df_area.drop(columns=['other'], errors='ignore')

        hill_numbers_area = []
        for index, row in df_area.iterrows():
            proportions = row[1:] / row[1:].sum()
            total_sum = row[1:].sum()
            hill_number_0, hill_number_1, hill_number_2 = calculate_hill_numbers(proportions)
            hill_numbers_area.append(
                [hill_number_0, hill_number_1, hill_number_2, total_sum] + proportions.values.tolist())

        df_area["Hill_0"] = [x[0] for x in hill_numbers_area]
        df_area["Hill_1"] = [x[1] for x in hill_numbers_area]
        df_area["Hill_2"] = [x[2] for x in hill_numbers_area]
        df_area["sum"] = [x[3] for x in hill_numbers_area]

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        # Save detailed results
        output_file_path = os.path.join(output_directory, file_name)
        df_area.to_csv(output_file_path, index=False)

        print(f"Calculation completed, results for '{continent} {year} {file_name}' saved as '{output_file_path}'")
        return True
    except Exception as e:
        print(f"Error occurred while processing file '{continent} {year} {file_name}': {e}")
        return False


# Define the list of continents to loop through
continents = ["Asia", "Europe", "North America", "Latin America", "Africa", "Oceania"]


def main():
    # Set number of processes (adjust based on your CPU cores)
    num_processes = os.cpu_count() or 4

    with Pool(processes=num_processes) as pool:
        for continent in continents:
            # Base input and output directory paths
            base_input_directory = fr"..\{continent}\your built-up area statistics input path"
            base_output_directory = fr"..\{continent}\your output path"

            # Loop through each year
            for year in range(2017, 2026):  # From 2017 to 2025
                input_directory = os.path.join(base_input_directory, str(year))

                # Get all CSV files
                file_names = [f for f in os.listdir(input_directory) if f.endswith('.csv')]

                # Use partial to fix some parameters
                process_func = functools.partial(
                    process_file,
                    continent,
                    year,
                    base_input_directory,
                    base_output_directory
                )

                # Process files in parallel
                results = pool.map(process_func, file_names)

                # Print statistics
                success_count = sum(results)
                print(f"{continent} {year}: Completed processing {success_count}/{len(file_names)} files")


if __name__ == '__main__':
    main()