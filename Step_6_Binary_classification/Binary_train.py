import pandas as pd
import os
from autogluon.tabular import TabularPredictor
from sklearn.model_selection import train_test_split

# Define the base path for input directory and range of years
base_directory = r'Your kernel density feature catalog'
years = range(2017, 2026)  # Include years from 2017 to 2025

# Iterate over each year
for year in years:
    input_directory = os.path.join(base_directory, str(year))  # Construct the full path for each year
    print(f"Processing directory: {input_directory}")

    # Initialize an empty DataFrame to store merged data
    combined_data = pd.DataFrame()

    # Iterate over all CSV files in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_directory, filename)  # Construct the full file path
            print(f"Processing file: {filename}")
            # Read data and skip the "FID" column
            data = pd.read_csv(file_path)  # Read all data first
            if 'FID' in data.columns:
                data = data.drop(columns=['FID'])  # Remove the "FID" column
            # Filter data, keeping rows where “bui_lab” is not “other”
            data = data[data['bui_lab'] != 'other']
            # Modify the "bui_lab" field
            data.loc[data['bui_lab'].isin(['other', 'residential']) == False, 'bui_lab'] = 'nonresidential'

            # Merge data
            combined_data = pd.concat([combined_data, data], ignore_index=True)
            print(f"Merged {len(data)} records; current total: {len(combined_data)}")

    # Check if there is any merged data
    if combined_data.empty:
        print(f"No valid data found in {input_directory}.")
        continue
    # Remove duplicates
    combined_data = combined_data.drop_duplicates()
    print(f"Number of rows after deduplication: {combined_data.shape[0]}")

    print(f"Number of rows in combined data: {combined_data.shape[0]}")

    # Define the label
    label = combined_data.columns[0]  # Assume the first column is the label
    print(f"Using label: {label}")

    # Split the dataset, 80% for training and validation, 20% for testing
    train_val_data, test_data = train_test_split(combined_data, test_size=0.2, random_state=42)
    print(f"Training and validation dataset rows: {train_val_data.shape[0]}, test dataset rows: {test_data.shape[0]}")

    # Further split out a 20% validation set from the training and validation data
    train_data, val_data = train_test_split(train_val_data, test_size=0.2, random_state=42)
    print(f"Training dataset rows: {train_data.shape[0]}, validation dataset rows: {val_data.shape[0]}")

    # Define training
    print("Starting model training...")
    predictor = TabularPredictor(label=label, eval_metric='accuracy').fit(train_data, tuning_data=val_data)
    print("Model training completed.")

    # Predict using the test dataset
    y_pred = predictor.predict(test_data.drop(columns=[label]))
    print("Prediction results:")
    print(y_pred.head())

    # Define evaluation
    evaluate = predictor.evaluate(test_data, silent=True)
    print("Evaluation results:")
    print(evaluate)

    # Save evaluation results to CSV
    eval_df = pd.DataFrame.from_dict(evaluate, orient='index', columns=['Score'])
    eval_file_path = os.path.join(r'Your save directory', f'evaluate_Binary_{year}.csv')
    eval_df.to_csv(eval_file_path)
    print(f"Evaluation results saved as: {eval_file_path}")

    # Model comparison
    leaderboard = predictor.leaderboard(test_data)
    print("Model comparison results:")
    print(leaderboard)

    # Save the model to a specified path
    model_folder = r'Your save directory'  # Create a subdirectory to save the model for that year
    os.makedirs(model_folder, exist_ok=True)  # Create the directory, do not raise an error if it already exists

    model_name = os.path.join(model_folder, f"Binary_model_{year}")  # Custom full path for the model
    predictor.save(model_name)  # Save the model
    print(f"Model saved as: {model_name}")