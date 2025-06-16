import os
import pandas as pd
import h2o
import json
import logging
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_latest_model_from_folder(folder_path: str) -> Optional[str]:
    latest_model = None
    latest_key: Tuple[int, int] = (0, 0)

    logging.info(f"Scanning folder: {folder_path} for latest model...")
    if not os.path.isdir(folder_path):
        logging.warning(f"Folder not found: {folder_path}. Cannot find model.")
        return None

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
                    logging.warning(f"Skipping malformed file: {filename}")
                    continue
    
    if latest_model:
        logging.info(f"Identified latest model: {latest_model} with key: {latest_key}")
    else:
        logging.info("No matching GBM_model_python_*.zip found in the folder.")
    return latest_model

def init():
    global model

    logging.info("Initializing H2O...")
    try:
        h2o.init()
        logging.info("H2O initialized.")
    except Exception as e:
        logging.error(f"Failed to initialize H2O: {e}", exc_info=True)
        raise RuntimeError("H2O initialization failed.")

    model_dir = os.getenv("AZUREML_MODEL_DIR")
    if not model_dir:
        logging.warning("AZUREML_MODEL_DIR environment variable not set. Falling back to current directory for local testing.")
        model_dir = "."

    model_folder_for_scan = model_dir

    model_filename = get_latest_model_from_folder(model_folder_for_scan)

    if not model_filename:
        logging.error(f"Could not find any matching MOJO model in {model_folder_for_scan}.")
        raise FileNotFoundError(f"No H2O MOJO model found in {model_folder_for_scan}.")

    model_path = os.path.join(model_folder_for_scan, model_filename)

    logging.info(f"Attempting to load MOJO model from: {model_path}")

    try:
        model = h2o.import_mojo(model_path)
        logging.info("Model loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load H2O MOJO model from {model_path}: {e}", exc_info=True)
        raise RuntimeError(f"Model loading failed: {e}")

def run(data):
    try:
        if isinstance(data, str):
            data_dict = json.loads(data)
        elif isinstance(data, dict):
            data_dict = data
        else:
            raise ValueError("Unsupported input format. Expected JSON string or dictionary.")

        records = data_dict.get("data", [])
        if not records:
            logging.warning("Input 'data' key is empty or not found.")
            return json.dumps({"error": "Input 'data' key is empty or not found. Provide data as a list of records."})

        df = pd.DataFrame(records)
        h2o_df = h2o.H2OFrame(df)
        predictions = model.predict(h2o_df)
        result_json = predictions.as_data_frame().to_json(orient="records")
        logging.info("Prediction successful.")
        return result_json

    except Exception as e:
        logging.exception("Prediction failed during run function:")
        return json.dumps({"error": str(e)})