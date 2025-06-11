
import os
import pandas as pd
import h2o
import json

def init():
    import logging
    global model

    # Initialize H2O
    h2o.init()

    # Use current directory if AZUREML_MODEL_DIR is not set
    model_dir = os.getenv("AZUREML_MODEL_DIR") or "."
    model_path = os.path.join(model_dir, "GBM_model_python_1749296476765_1.zip")

    print("Loading MOJO model from:", model_path)

    try:
        # Load the H2O MOJO model
        model = h2o.import_mojo(model_path)
        print("Model loaded successfully.")
    except Exception as e:
        logging.error(f"Failed to load H2O MOJO model: {e}")
        raise RuntimeError("Model loading failed.")
def run(data):
    import logging
    import json
    import pandas as pd

    try:
        # Parse input JSON string to dictionary
        if isinstance(data, str):
            data_dict = json.loads(data)  # JSON string → dict
        elif isinstance(data, dict):
            data_dict = data
        else:
            raise ValueError("Unsupported input format")

        # Extract the 'data' key which contains a list of records
        records = data_dict.get("data", [])

        # Convert to Pandas DataFrame first
        df = pd.DataFrame(records)

        # Then convert to H2OFrame
        h2o_df = h2o.H2OFrame(df)

        # Use model loaded in init (no need to reload)
        predictions = model.predict(h2o_df)

        return predictions.as_data_frame().to_json(orient="records")

    except Exception as e:
        logging.exception("Prediction failed")
        return json.dumps({"error": str(e)})
