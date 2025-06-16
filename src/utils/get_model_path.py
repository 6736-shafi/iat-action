import os
import re
from datetime import datetime

def get_latest_mojo_model(folder_path: str) -> str | None:
    """
    Finds the H2O MOJO model file with the latest timestamp in a given folder.

    Assumes model filenames follow the pattern: 'my_h2o_model_YYYYMMDD_HHMMSS.zip'.

    Args:
        folder_path (str): The path to the directory containing the MOJO models.

    Returns:
        str | None: The full path to the latest MOJO model file, or None if no
                    matching models are found.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist or is not a directory.")
        return None

    latest_model_path = None
    latest_timestamp = None

    # Regex to match the pattern 'my_h2o_model_YYYYMMDD_HHMMSS.zip'
    # We capture the timestamp part
    model_pattern = re.compile(r"my_h2o_model_(\d{8}_\d{6})\.zip")

    for filename in os.listdir(folder_path):
        match = model_pattern.match(filename)
        if match:
            # Extract the timestamp string from the filename
            timestamp_str = match.group(1) # This will be like 'YYYYMMDD_HHMMSS'
            try:
                # Convert the timestamp string to a datetime object for comparison
                current_file_timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                # If it's the first matching model, or newer than the current latest
                if latest_timestamp is None or current_file_timestamp > latest_timestamp:
                    latest_timestamp = current_file_timestamp
                    
                    latest_model = filename
            except ValueError:
                # This handles cases where a file matches the regex pattern but
                # has an invalid date format (e.g., 'my_h2o_model_20239999_000000.zip')
                print(f"Warning: Skipping file '{filename}' due to invalid timestamp format.")
                continue

    
    
    return './model/'+latest_model


    

   

  

    
    

