
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







# import os
# import pandas as pd
# import h2o
# import json
# import logging # It's good to explicitly import logging

# # Remove these lines, they are for local environment discovery and won't work in the container
# # from utils.get_model_path import get_latest_mojo_model
# # latest_model = get_latest_mojo_model('../model')
# # model_name = os.path.basename(latest_model)


# def init():
#     global model
    
#     # Initialize H2O (already correctly done)
#     h2o.init()

#     # Get the model directory provided by Azure ML
#     # This path is where your registered model (my-h2o-cicd-model/17) is mounted.
#     model_dir = os.getenv("AZUREML_MODEL_DIR") 
    
#     # Check if model_dir is correctly set (it should be)
#     if not model_dir:
#         logging.error("AZUREML_MODEL_DIR environment variable not found.")
#         raise RuntimeError("Model directory not specified by Azure ML.")

#     # List contents of the mounted model directory to find the actual MOJO file
#     # The MOJO model is typically the only .zip file in the mounted directory.
#     # We'll search for the first .zip file.
#     model_filename = None
#     for filename in os.listdir(model_dir):
#         if filename.endswith(".zip"):
#             model_filename = filename
#             break
            
#     if not model_filename:
#         logging.error(f"No .zip H2O MOJO model found in the mounted directory: {model_dir}")
#         raise RuntimeError("H2O MOJO model .zip file not found in deployment.")

#     model_path = os.path.join(model_dir, model_filename)

#     print("Loading MOJO model from:", model_path)
#     logging.info(f"Attempting to load model from: {model_path}") # Use logging for better visibility

#     try:
#         # Load the H2O MOJO model
#         model = h2o.import_mojo(model_path)
#         print("Model loaded successfully.")
#         logging.info("H2O Model loaded successfully.")
#     except Exception as e:
#         logging.error(f"Failed to load H2O MOJO model from {model_path}: {e}")
#         raise RuntimeError("Model loading failed.") from e # Use 'from e' for better traceback

# def run(data):
#     # Your run function looks good for processing JSON input
#     import logging
#     import json
#     import pandas as pd

#     try:
#         if isinstance(data, str):
#             data_dict = json.loads(data)
#         elif isinstance(data, dict):
#             data_dict = data
#         else:
#             raise ValueError("Unsupported input format")

#         records = data_dict.get("data", [])
#         df = pd.DataFrame(records)
#         h2o_df = h2o.H2OFrame(df)
#         predictions = model.predict(h2o_df)
#         return predictions.as_data_frame().to_json(orient="records")

#     except Exception as e:
#         logging.exception("Prediction failed") # logging.exception logs the error and traceback
#         return json.dumps({"error": str(e)})
