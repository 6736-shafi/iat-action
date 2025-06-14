









import argparse
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineDeployment, CodeConfiguration
import argparse
import sys
from pathlib import Path
import os
from dotenv import load_dotenv # Although not directly used with hardcoded values, good practice to keep for future flexibility

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, ClientSecretCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment
from azure.core.exceptions import ResourceNotFoundError # Import for catching specific exception (though less critical for create_or_update)

# ... (imports and get_ml_client function remain the same) ...


# new get_ml_client() for all component scripts
import os
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from config.connect import get_ml_client
client = get_ml_client()
print(client)

def main(endpoint_name, env_name_path, env_version_path, model_name_path, model_version_path, out_status_path=None):
    """
    Deploys a model to a managed online endpoint.
    """
    # client = get_ml_client()
    
    # Read the model name and version from the input files
    with open(model_name_path, 'r') as f:
        model_name = f.read().strip()
    with open(model_version_path, 'r') as f:
        model_version = f.read().strip()
        
    # FIX: Read the environment name and version from their respective input files
    with open(env_name_path, 'r') as f:
        env_name = f.read().strip()
    with open(env_version_path, 'r') as f:
        env_version = f.read().strip()

    print(f"Read model name '{model_name}' and version '{model_version}' for deployment.")
    print(f"Using environment '{env_name}' with version '{env_version}'.")

    # Define the code configuration
    code_cfg = CodeConfiguration(code="./", scoring_script="score.py")
    
    # Define the Managed Online Deployment
    deployment = ManagedOnlineDeployment(
        name="blue",
        endpoint_name=endpoint_name,
        model=f"azureml:{model_name}:{model_version}",
        environment=f"azureml:{env_name}:{env_version}", # Now using the values read from files
        code_configuration=code_cfg,
        instance_type="Standard_F2s_v2",
        instance_count=1,
    )
    
    # Begin the deployment process
    result = client.online_deployments.begin_create_or_update(deployment).result()
    state = result.provisioning_state
    
    print(f"Deployment '{result.name}' for endpoint '{endpoint_name}' has provisioning state: {state}")
    
    if out_status_path:
        with open(out_status_path, "w") as f:
            f.write(state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint_name", required=True)
    # FIX: Argument names now reflect they receive a path
    parser.add_argument("--environment_name", required=True, help="Path to file containing the environment name.")
    parser.add_argument("--environment_version", required=True, help="Path to file containing the environment version.")
    parser.add_argument("--model_name", required=True, help="Path to file containing the model name.")
    parser.add_argument("--model_version", required=True, help="Path to file containing the model version.")
    parser.add_argument("--deployment_status", required=True)
    args = parser.parse_args()
    
    main(
        args.endpoint_name,
        args.environment_name, # Pass the file path
        args.environment_version, # Pass the file path
        args.model_name,
        args.model_version,
        args.deployment_status
    )
