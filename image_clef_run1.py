# -*- coding: utf-8 -*-
"""Image clef - run1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u5J5mEMeQFtyBnCUD-IA8OC-F7IQpi4F
"""

from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

!cp -r '/content/drive/MyDrive/Touche clef/trainingset-ideology-power.zip' '/content/'

import pandas as pd
import zipfile
import io
import os

# Path to the zip file
zip_file_path = '/content/trainingset-ideology-power.zip'

# Function to read TSV files from a specific folder within a zip file and return a DataFrame
def read_tsv_from_zip_folder(zip_file_path, folder_name):
    dataframes = []
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.startswith(folder_name) and file_name.endswith('.tsv'):
                with zip_ref.open(file_name) as file:
                    # Read TSV file into DataFrame
                    df = pd.read_csv(io.TextIOWrapper(file, 'utf-8'), sep='\t')
                    # Append DataFrame to the list
                    dataframes.append(df)
    # Concatenate all DataFrames into one
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df

# Specify the folder name you want to extract files from
specific_folder_name = 'power'

# Call the function to read TSV files from the specified folder within the zip file
df = read_tsv_from_zip_folder(zip_file_path, specific_folder_name)

# Now, df contains the combined DataFrame from all TSV files in the specified folder within the zip file

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score
from sklearn.pipeline import make_pipeline
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

# Load data
train_data = df
test_data = df

# Prepare labels
train_labels = train_data['label']

# Replace NaN values in 'text_en' column with empty string in training and test data
train_data['text_en'] = train_data['text_en'].fillna('')
test_data['text_en'] = test_data['text_en'].fillna('')

# Split training data into training and validation sets
train_data, val_data, train_labels, val_labels = train_test_split(
    train_data['text_en'], train_labels, test_size=0.20, random_state=42
)

train_labels = df['label']

# Replace NaN values in 'text_en' column with empty string in training and test data
train_data = df['text_en'].fillna('')

# Define TfidfVectorizer for text data
vectorizer = TfidfVectorizer(
    max_features=10000, ngram_range=(1, 2), min_df=2, max_df=0.9, stop_words='english'
)

# Define class weights based on training labels
class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(train_labels), y=train_labels)
class_weights_dict = dict(enumerate(class_weights))

# Create a pipeline with TfidfVectorizer and LinearSVC model
model = make_pipeline(vectorizer, LinearSVC(class_weight=class_weights_dict))

# Define hyperparameter grid for tuning
param_grid = {
    'linearsvc__C': [0.1, 1],  # Try a range of C values
    'linearsvc__max_iter': [1000, 1700, 2500],  # Different max iterations
}

# Use GridSearchCV to tune the model
grid_search = GridSearchCV(model, param_grid, scoring='f1', cv=5, verbose=3)
grid_search.fit(train_data, train_labels)

# Best model found by GridSearchCV
best_model = grid_search.best_estimator_

# Predict on the validation set
val_predictions = best_model.predict(val_data)

# Calculate F1 score on the validation set
val_f1 = f1_score(val_labels, val_predictions)
print("Validation F1 Score:", val_f1)

# Predict on the test data
test_predictions = best_model.predict(test_data['text_en'])

# Create a DataFrame with the predictions
output_df = pd.DataFrame({'id': test_data['id'], 'label': test_predictions})

# Save the DataFrame to a CSV file
output_df.to_csv('predictions.csv', index=False)
print("Predictions saved to predictions.csv")

val_f2 = f1_score(df['label'], test_predictions)
print(val_f2)

import joblib
joblib.dump(best_model, 'power linearsvc f1-73.joblib')
print("Model saved to best_model.joblib")

import zipfile

# Specify the path to the zip file
zip_file_path = '/content/ideology-power-st-testset.zip'

# Specify the directory where you want to extract the files
extract_dir = 'content/'

# Create a ZipFile object
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    # Extract all the contents of the zip file
    zip_ref.extractall(extract_dir)

print("Files extracted successfully to", extract_dir)

import pandas as pd

# Path to the TSV file
file_path = '/content/content/power/power-es-test.tsv'
fpath='pixel-power-es-run1.tsv'

# Read the TSV file into a DataFrame
df = pd.read_csv(file_path, sep='\t')

# Display the DataFrame
print(df)

import pandas as pd
import joblib  # Import joblib for loading the model
all="ua"
fpath="pixel-power-"+all+"-run2.tsv"
file_path = "/content/content/power/power-"+all+"-test.tsv"

# Read the TSV file into a DataFrame
df = pd.read_csv(file_path, sep='\t')

# Load the saved model using joblib # Replace 'best_model.joblib' with the path to your saved model file
# Load test data
test_data = df  # Replace 'your_test_data.csv' with your test data file path

# Replace NaN values in 'text_en' column with empty string in test data
test_data['text_en'] = test_data['text_en'].fillna('')

# Predict on the test data using the loaded model
test_predictions = model.predict(test_data['text_en'])

# Create a DataFrame with the predictions
output_df = pd.DataFrame({'id': test_data['id'], 'label': test_predictions})

# Save the DataFrame to a CSV file
output_df.to_csv(fpath, sep='\t', columns=['id', 'label'], header=False, index=False)
print("Predictions saved to ",fpath)