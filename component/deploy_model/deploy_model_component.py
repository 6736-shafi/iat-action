import argparse
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import ManagedOnlineDeployment, CodeConfiguration

import sys
from pathlib import Path

# Add the parent directory to sys.path
sys.path.append(str(Path.cwd().parent))
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
# Import the function
# from config.connection import get_ml_client

def main(endpoint_name, env_name, env_version, model_name_path, model_version_path, out_status_path=None):
    """
    Deploys a model to a managed online endpoint.

    Args:
        endpoint_name (str): The name of the existing online endpoint.
        env_name (str): The name of the environment to use.
        env_version (str): The version of the environment.
        model_name_path (str): Path to the file containing the registered model name.
        model_version_path (str): Path to the file containing the registered model version.
        out_status_path (str, optional): Path to write the final deployment state.
    """
    client = get_ml_client()
    
    # FIX: Read the model name and version from the input files passed by the previous step.
    with open(model_name_path, 'r') as f:
        model_name = f.read().strip()
    with open(model_version_path, 'r') as f:
        model_version = f.read().strip()

    print(f"Read model name '{model_name}' and version '{model_version}' for deployment.")

    # Define the code configuration, assuming score.py is in the same folder
    code_cfg = CodeConfiguration(code="./", scoring_script="score.py")
    
    # Define the Managed Online Deployment
    deployment = ManagedOnlineDeployment(
        name="blue",  # Or another color like 'green' for blue-green deployment
        endpoint_name=endpoint_name,
        model=f"azureml:{model_name}:{model_version}",
        environment=f"azureml:{env_name}:{env_version}",
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
    parser.add_argument("--environment_name", required=True)
    parser.add_argument("--environment_version", required=True)
    # These arguments will receive the *path* to the files with the actual values
    parser.add_argument("--model_name", required=True, help="Path to file containing the model name.")
    parser.add_argument("--model_version", required=True, help="Path to file containing the model version.")
    parser.add_argument("--deployment_status", required=True)
    args = parser.parse_args()
    
    main(
        args.endpoint_name,
        args.environment_name,
        args.environment_version,
        args.model_name,
        args.model_version,
        args.deployment_status
    )