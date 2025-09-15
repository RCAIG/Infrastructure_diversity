import os
import zipfile

def unzip_files_in_directory(directory):
    # Traverse all files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is a zip archive
            if file.endswith('.zip'):
                file_path = os.path.join(root, file)
                # Specify the extraction target folder as the same directory
                target_directory = os.path.join(root, os.path.splitext(file)[0])

                # Ensure the target folder exists
                os.makedirs(target_directory, exist_ok=True)

                # Open the zip file and extract, handling potential errors
                try:
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        # Extract the contents
                        zip_ref.extractall(target_directory)
                    print(f'File extracted: {file_path} -> {target_directory}')
                except Exception as e:
                    print(f'Error during extraction: {file_path} - Error: {e}')

# Specify the directory path to be extracted
directory_path = r'Your OSM compressed package directory'
unzip_files_in_directory(directory_path)