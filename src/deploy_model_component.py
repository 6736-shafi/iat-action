# import argparse
# import sys
# from pathlib import Path
# import os
# from dotenv import load_dotenv

# from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, ClientSecretCredential
# from azure.ai.ml import MLClient
# from azure.ai.ml.entities import ManagedOnlineDeployment, CodeConfiguration, ManagedOnlineEndpoint
# from azure.core.exceptions import ResourceNotFoundError # Import for catching specific exception


# def get_ml_client():
#     """
#     Authenticates and returns an MLClient.
#     Prioritizes ClientSecretCredential (for service principal) with hardcoded values,
#     otherwise falls back to DefaultAzureCredential.
#     """
#     # --- WARNING: HARDCODING CREDENTIALS IS NOT RECOMMENDED FOR PRODUCTION ---
#     # This is for temporary testing only. For secure applications, use environment variables
#     # or Azure Key Vault to manage secrets.

#     tenant_id = "084a029e-1435-40bc-8201-87ec1b251fb3"
#     client_id = "bd13c2e3-28bc-4e29-bc12-1d2461071a68"
#     client_secret = "ea16e983-e747-4651-8c01-537e56638875"


#     # Your Azure subscription, resource group, and workspace details
#     subscription_id = "6bd1f99e-e7cb-4226-b9d5-09433d793bda"
#     resource_group_name = "shafi1"
#     workspace_name = "shafi1"

#     # Use ClientSecretCredential with the hardcoded values
#     print("Attempting authentication with hardcoded Service Principal credentials...")
#     credential = ClientSecretCredential(
#         tenant_id=tenant_id,
#         client_id=client_id,
#         client_secret=client_secret
#     )
#     # The DefaultAzureCredential fallback path is now less likely to be hit,
#     # but the structure remains if you decide to uncomment it later.
#     try:
#         # Attempt to get a token to verify the hardcoded credentials
#         credential.get_token("https://management.azure.com/.default")
#         print("Hardcoded Service Principal authentication successful.")
#     except Exception as e:
#         print(f"Hardcoded Service Principal authentication failed: {e}.")
#         print("Falling back to DefaultAzureCredential (which may prompt for interactive login if no other credentials are found)...")
#         try:
#             credential = DefaultAzureCredential()
#             credential.get_token("https://management.azure.com/.default")
#             print("DefaultAzureCredential successful.")
#         except Exception as inner_e:
#             print(f"DefaultAzureCredential also failed: {inner_e}. Falling back to InteractiveBrowserCredential...")
#             credential = InteractiveBrowserCredential()


#     # Initialize MLClient
#     return MLClient(
#         credential=credential,
#         subscription_id=subscription_id,
#         resource_group_name=resource_group_name,
#         workspace_name=workspace_name
#     )

# # Add the parent directory to sys.path if this script is part of a larger project structure
# sys.path.append(str(Path.cwd().parent))

# def main(endpoint_name, env_name, env_version, model_name, model_version, out_status_path=None, input_tasks=None):
#     """
#     Ensures an online endpoint exists and then deploys a model to it.

#     Args:
#         endpoint_name (str): The name of the online endpoint to create or update.
#         env_name (str): The name of the environment to use.
#         env_version (str): The version of the environment.
#         model_name (str): The registered model name.
#         model_version (str): The registered model version.
#         out_status_path (str, optional): Path to write the final deployment state.
#         input_tasks (str, optional): A placeholder argument for input tasks.
#     """
#     client = get_ml_client()

#     print(f"Using model name '{model_name}' and version '{model_version}' for deployment.")

#     # Placeholder for input_tasks usage
#     if input_tasks:
#         print(f"Received input_tasks: {input_tasks}. Further logic can be added here.")

#     # --- Step 1: Ensure the online endpoint exists ---
#     print(f"Checking for endpoint '{endpoint_name}'...")
#     try:
#         # Attempt to get the endpoint to see if it exists
#         endpoint = client.online_endpoints.get(name=endpoint_name)
#         print(f"Endpoint '{endpoint_name}' already exists.")
#     except ResourceNotFoundError:
#         print(f"Endpoint '{endpoint_name}' not found. Creating a new one...")
#         # Define the online endpoint object
#         endpoint = ManagedOnlineEndpoint(
#             name=endpoint_name,
#             description="Online endpoint for model deployment via script",
#             auth_mode="key" # You can choose "key" or "aml_token"
#         )
#         try:
#             # Create the endpoint
#             client.online_endpoints.begin_create_or_update(endpoint).result()
#             print(f"Endpoint '{endpoint_name}' created successfully.")
#         except Exception as e:
#             print(f"Error creating endpoint '{endpoint_name}': {e}")
#             sys.exit(1) # Exit if endpoint creation fails
#     except Exception as e:
#         print(f"An unexpected error occurred while checking for endpoint '{endpoint_name}': {e}")
#         sys.exit(1)


#     # --- Step 2: Define and create/update the deployment on the endpoint ---
#     # Ensure score.py exists in the same directory as this script.
#     if not os.path.exists("./score.py"):
#         print("Warning: 'score.py' not found in the current directory. Deployment might fail if scoring script is missing.")
#         # Consider adding sys.exit(1) here if score.py is mandatory for every deployment
#     code_cfg = CodeConfiguration(code="./", scoring_script="score.py")

#     # Define the Managed Online Deployment
#     deployment = ManagedOnlineDeployment(
#         name="blue",  # Or another color like 'green' for blue-green deployment
#         endpoint_name=endpoint_name,
#         model=f"azureml:{model_name}:{model_version}",
#         environment=f"azureml:{env_name}:{env_version}",
#         code_configuration=code_cfg,
#         instance_type="Standard_F2s_v2",
#         instance_count=1,
#     )

#     # Begin the deployment process
#     print(f"Submitting deployment '{deployment.name}' to endpoint '{endpoint_name}'...")
#     try:
#         result = client.online_deployments.begin_create_or_update(deployment).result()
#         state = result.provisioning_state

#         print(f"Deployment '{result.name}' for endpoint '{endpoint_name}' has provisioning state: {state}")

#         if out_status_path:
#             with open(out_status_path, "w") as f:
#                 f.write(state)
#             print(f"Deployment status written to: {out_status_path}")
#     except Exception as e:
#         print(f"An error occurred during deployment: {e}")
#         if out_status_path:
#             with open(out_status_path, "w") as f:
#                 f.write(f"FAILED: {e}")
#         sys.exit(1) # Exit with an error code

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Deploy a model to an Azure ML managed online endpoint.")
#     parser.add_argument("--endpoint_name", required=True, help="The name of the existing online endpoint.")
#     parser.add_argument("--environment_name", required=True, help="The name of the environment to use.")
#     parser.add_argument("--environment_version", required=True, help="The version of the environment.")
#     parser.add_argument("--model_name", required=True, help="The registered model name.")
#     parser.add_argument("--model_version", required=True, help="The registered model version.")
#     parser.add_argument("--deployment_status", required=True, help="Path to write the final deployment state.")
#     parser.add_argument("--input_tasks", help="An optional argument for input tasks.")
#     args = parser.parse_args()

#     main(
#         args.endpoint_name,
#         args.environment_name,
#         args.environment_version,
#         args.model_name,
#         args.model_version,
#         args.deployment_status,
#         args.input_tasks # Pass input_tasks to the main function if present
#     )










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
