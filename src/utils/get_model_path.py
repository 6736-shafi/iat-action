import os
from typing import Optional, Tuple

def get_latest_model_from_folder(folder_path: str) -> Optional[str]:
    latest_model = None
    latest_key: Tuple[int, int] = (0, 0)  # (timestamp, version)

    for filename in os.listdir(folder_path):
        if filename.startswith("GBM_model_python") and filename.endswith(".zip"):
            parts = filename.split("_")
            if len(parts) >= 5:
                try:
                    timestamp = int(parts[3])
                    version_with_ext = parts[4]
                    version = int(version_with_ext.split(".")[0])
                    current_key = (timestamp, version)
                    if current_key > latest_key:
                        latest_key = current_key
                        latest_model = filename
                except ValueError:
                    continue  # skip malformed files

    return latest_model

    
# print(get_latest_model_from_folder('../../model') ) # Example usage, adjust path as needed