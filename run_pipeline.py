import os
# from dotenv import load_dotenv # <<< CRITICAL: Keep this line commented out or remove it!

from azure.identity import ClientSecretCredential
from azure.ai.ml import MLClient

def get_ml_client() -> MLClient:
    """
    Authenticates to Azure Machine Learning workspace using a Service Principal
    and returns an MLClient object.

    Expects the following environment variables to be set:
    - TENANT_ID: Your Azure Active Directory tenant ID.
    - CLIENT_ID: The client ID (Application ID) of your Service Principal.
    - CLIENT_SECRET: The client secret of your Service Principal.
    - SUBSCRIPTION_ID: Your Azure subscription ID.
    - RESOURCE_GROUP_NAME: The name of the resource group where your AML workspace resides.
    - WORKSPACE_NAME: The name of your Azure Machine Learning workspace.

    Returns:
        MLClient: An authenticated MLClient object to interact with your workspace.
    """
    print("--- Inside get_ml_client() (Azure ML Component Context / Python Process) ---")
    # In Azure ML components, environment variables are passed directly to the container runtime.
    # load_dotenv() is not needed and can interfere.

    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    subscription_id = os.getenv("SUBSCRIPTION_ID")
    resource_group_name = os.getenv("RESOURCE_GROUP_NAME")
    workspace_name = os.getenv("WORKSPACE_NAME")

    # Debugging: Print what os.getenv() sees inside this Python process
    print(f"Python sees TENANT_ID: {tenant_id}")
    print(f"Python sees CLIENT_ID: {client_id}")
    print(f"Python sees CLIENT_SECRET: {'*' * len(client_secret) if client_secret else 'None'}") # Mask secret
    print(f"Python sees SUBSCRIPTION_ID: {subscription_id}")
    print(f"Python sees RESOURCE_GROUP_NAME: {resource_group_name}")
    print(f"Python sees WORKSPACE_NAME: {workspace_name}")
    print("--------------------------------------------------------------------------")

    # Basic validation that environment variables are set
    if not all([tenant_id, client_id, client_secret, subscription_id, resource_group_name, workspace_name]):
        raise ValueError(
            "One or more required environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET, "
            "SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, WORKSPACE_NAME) are not set inside the Azure ML component."
        )

    # Authenticate using ClientSecretCredential
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    ml_client = MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name,
    )
    return ml_client
