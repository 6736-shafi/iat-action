import argparse
import sys
from pathlib import Path
import os
from dotenv import load_dotenv # Although not directly used with hardcoded values, good practice to keep for future flexibility

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, ClientSecretCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment
from azure.core.exceptions import ResourceNotFoundError # Import for catching specific exception (though less critical for create_or_update)
from config.connect import get_ml_client

import os
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

# --- Retrieve environment variables *inside* run_pipeline.py ---
# These variables are set by the 'env' block in your GitHub Actions workflow.
subscription_id = os.environ.get("SUBSCRIPTION_ID")
resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
workspace_name = os.environ.get("WORKSPACE_NAME")

# --- Add robust checks to ensure variables are present and not empty ---
missing_vars = []
if not subscription_id: # Checks for None or empty string
    missing_vars.append("SUBSCRIPTION_ID")
if not resource_group_name: # Checks for None or empty string
    missing_vars.append("RESOURCE_GROUP_NAME")
if not workspace_name: # Checks for None or empty string
    missing_vars.append("WORKSPACE_NAME")

if missing_vars:
    raise ValueError(
        f"Missing or empty required Azure ML environment variables: "
        f"{', '.join(missing_vars)}. "
        f"Please ensure they are set in your GitHub workflow secrets "
        f"and correctly passed to the 'Run Pipeline' step."
    )

# --- Initialize MLClient by passing the retrieved values ---
ml_client = get_ml_client(subscription_id, resource_group_name, workspace_name)
print("🎯 MLClient created successfully.")


def main(env_name, conda_file_path, out_name_path, out_version_path):
    """
    Creates or updates an Azure ML Environment.

    Args:
        env_name (str): The name for the environment.
        conda_file_path (str): The local path to the conda.yaml file.
        out_name_path (str): Path to write the environment name output.
        out_version_path (str): Path to write the environment version output.
    """
    # ml_client = get_ml_client()

    print(f"Creating or updating environment '{env_name}'...")

    # --- Step 1: Validate conda_file_path exists ---
    if not os.path.exists(conda_file_path):
        print(f"Error: Conda file not found at '{conda_file_path}'. Please ensure the path is correct.")
        sys.exit(1)

    # Define the Environment object
    env = Environment(
        name=env_name,
        description="Custom environment for H2O model deployment from pipeline.",
        conda_file=conda_file_path,
        image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"
    )

    # --- Step 2: Create or update the environment in the workspace with error handling ---
    try:
        created_env = ml_client.environments.create_or_update(env)
        print(f"Successfully created environment '{created_env.name}' with version '{created_env.version}'")

        # --- Step 3: Write the outputs for subsequent pipeline steps ---
        # Ensure output directories exist
        os.makedirs(os.path.dirname(out_name_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(out_version_path) or '.', exist_ok=True)

        with open(out_name_path, "w") as f:
            f.write(created_env.name)
            print(f"Environment name written to: {out_name_path}")

        with open(out_version_path, "w") as f:
            f.write(str(created_env.version))
            print(f"Environment version written to: {out_version_path}")

    except Exception as e:
        print(f"An error occurred during environment creation or update: {e}")
        # Optionally, write a failure status to output paths
        if out_name_path:
            os.makedirs(os.path.dirname(out_name_path) or '.', exist_ok=True)
            with open(out_name_path, "w") as f:
                f.write(f"FAILED: {e}")
        if out_version_path:
            os.makedirs(os.path.dirname(out_version_path) or '.', exist_ok=True)
            with open(out_version_path, "w") as f:
                f.write(f"FAILED: {e}")
        sys.exit(1) # Exit with an error code

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create or update an Azure ML Environment.")
    parser.add_argument("--environment_name", required=True, help="Name of the environment to create.")
    parser.add_argument("--conda_file", required=True, help="Path to the conda dependency file (e.g., ./conda.yaml).")
    parser.add_argument("--created_env_name", required=True, help="Output path for the environment name (e.g., ./env_name.txt).")
    parser.add_argument("--created_env_version", required=True, help="Output path for the environment version (e.g., ./env_version.txt).")
    args = parser.parse_args()
    
    main(
        args.environment_name,
        args.conda_file,
        args.created_env_name,
        args.created_env_version
    )


















