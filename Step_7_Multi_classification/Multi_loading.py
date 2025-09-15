import os
import pandas as pd
from autogluon.tabular import TabularPredictor

# Define the model path
model_path = r'your model path'

# Define the range of years
years = range(2017, 2026)  # From 2017 to 2025

for year in years:
    # Dynamically construct input and output directories
    input_directory = fr'your kernel density feature path{year}'
    output_directory = fr'your prediction result output path{year}'

    # Create output directory (if it does not exist)
    os.makedirs(output_directory, exist_ok=True)

    # Load the pre-trained model
    predictor = TabularPredictor.load(model_path.format(year))

    # Iterate over all CSV files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_directory, filename)  # Full file path
            print(f"Processing file: {filename} ({year})")

            try:
                # Read the CSV file
                data = pd.read_csv(file_path)
                if 'FID' in data.columns:
                    data = data.drop(columns=['FID'])
                # Get the label column name
                label = data.columns[0]
                # Make predictions, assuming all columns except the label column are used for prediction
                predictions = predictor.predict(data.drop(columns=[label]))

                # Create output file path
                output_file_path = os.path.join(output_directory, f'predicted_{filename}')

                # Save the prediction results to a new CSV file
                predictions.to_csv(output_file_path, index=False)
                print(f"Prediction results saved to: {output_file_path}")

            except Exception as e:
                print(f"Error occurred while processing file {filename}: {e}")

print("All files processed.")