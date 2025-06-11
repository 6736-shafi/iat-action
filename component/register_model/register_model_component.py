import os
import argparse
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model
import sys
from pathlib import Path
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.identity import InteractiveBrowserCredential

def get_ml_client():
    """Authenticates and returns an MLClient."""
    try:
        credential = DefaultAzureCredential()
        # Check if the credential can get a token.
        credential.get_token("https://management.azure.com/.default")
    except Exception:
        # Fall back to interactive credential if default fails.
        credential = InteractiveBrowserCredential()
    
    # Replace with your subscription, resource group, and workspace details
    return MLClient(
        credential=credential,
        subscription_id="6bd1f99e-e7cb-4226-b9d5-09433d793bda",
        resource_group_name="shafi1",
        workspace_name="shafi1"
    )


import inspect, os

# This gets the file that contains the current function (if inside a module)
current_file = inspect.getfile(inspect.currentframe())
current_folder = os.path.dirname(os.path.abspath(current_file))
register_py = os.path.join(current_folder, "..", "config", "connection.py")

def main(model_path, model_name, out_name_path, out_version_path):
    """
    Registers a model in the Azure ML workspace.

    Args:
        model_path (str): The local path to the model artifact.
        model_name (str): The name to register the model under.
        out_name_path (str): Path to the output file to write the registered model name.
        out_version_path (str): Path to the output file to write the registered model version.
    """
    ml_client = get_ml_client()
    
    print(f"Looking for model at: {model_path}")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file or directory not found at path: {model_path}")

    # Create a Model entity
    model_to_register = Model(
        path=model_path,
        name=model_name,
        description="Model registered from CI/CD pipeline."
    )
    
    # Register the model
    registered_model = ml_client.models.create_or_update(model_to_register)
    
    print(f"Registered model: {registered_model.name} with version: {registered_model.version}")
    
    # Write outputs for subsequent pipeline steps
    with open(out_name_path, "w") as f:
        f.write(registered_model.name)
        
    with open(out_version_path, "w") as f:
        f.write(str(registered_model.version))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", required=True, help="Path to the model file or folder.")
    parser.add_argument("--model_name", required=True, help="Name of the model to register.")
    parser.add_argument("--registered_model_name", required=True, help="Output path for the registered model name.")
    parser.add_argument("--registered_model_version", required=True, help="Output path for the registered model version.")
    args = parser.parse_args()
    
    main(
        args.model_path, 
        args.model_name,
        args.registered_model_name,
        args.registered_model_version
    )