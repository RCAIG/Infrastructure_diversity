import pandas as pd
from transformers import pipeline

# Read the CSV file
df = pd.read_csv(r'Original data path')  # Replace with your CSV file path

# Create a zero-shot classification pipeline
classifier = pipeline("zero-shot-classification")

# Define the candidate labels
candidate_labels = ["Residential", "Commercial", "Industrial", "Education", "Medical", "Public", "Other"]

# Function to classify each text
def classify_text(text):
    result = classifier(text, candidate_labels=candidate_labels, multi_label=False)
    # Print the text and predicted label for each row
    print(f"Text: {text} -> pre_label: {result['labels'][0]}")
    return result

# Apply classification function to the DataFrame
df['predicted_category'] = df['Category field (name or description)'].apply(classify_text)

# Extract the most probable category from the classification results
df['predicted_category'] = df['predicted_category'].apply(lambda x: x['labels'][0])

# Output results to the console
print(df[['Category field (name or description)', 'predicted_category']])

# Save the results to a new CSV file
output_file_path = r'Target Path'
df.to_csv(output_file_path, index=False, encoding='utf-8-sig')