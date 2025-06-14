import os
from dotenv import load_dotenv

from azure.ai.ml import MLClient


# Load environment variables from .env file for local development purposes.
# In GitHub Actions, environment variables are set directly and override .env.
load_dotenv()


from azure.identity import ClientSecretCredential

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
    # Service principal details (retrieved from environment variables)
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
    resource_group_name = os.getenv("AZURE_RESOURCE_GROUP")
    workspace_name = os.getenv("AZURE_WORKSPACE")

    # Basic validation that environment variables are set
    if not all([tenant_id, client_id, client_secret, subscription_id, resource_group_name, workspace_name]):
        raise ValueError(
            "One or more required environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET, "
            "SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, WORKSPACE_NAME) are not set."
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
