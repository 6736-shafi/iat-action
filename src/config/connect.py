import os
from dotenv import load_dotenv
from azure.identity import (
    DefaultAzureCredential,
    InteractiveBrowserCredential,
    ClientSecretCredential
)
from azure.ai.ml import MLClient
from azure.core.exceptions import ClientAuthenticationError

# Load environment variables from .env file for local development purposes.
# In GitHub Actions, environment variables are set directly and override .env.
load_dotenv()

def get_ml_client(subscription_id: str, resource_group_name: str, workspace_name: str):
    """
    Authenticates and returns an MLClient using provided workspace details.
    It attempts Service Principal authentication, then falls back to DefaultAzureCredential.
    InteractiveBrowserCredential is a fallback mainly for local interactive use.

    Args:
        subscription_id (str): The Azure subscription ID.
        resource_group_name (str): The Azure resource group name where the ML workspace resides.
        workspace_name (str): The Azure Machine Learning workspace name.

    Returns:
        MLClient: An authenticated Azure Machine Learning client.

    Raises:
        Exception: If no suitable credential can be obtained.
    """

    # Retrieve service principal credentials from environment variables.
    # These are typically set as GitHub secrets and provided to the workflow.
    # The 'creds' input to azure/login sets up DefaultAzureCredential implicitly.
    tenant_id = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    credential = None

    print("Trying authentication with Service Principal credentials (via ClientSecretCredential)...")
    try:
        # Attempt ClientSecretCredential only if all necessary environment variables are set.
        # This branch will typically be skipped in GitHub Actions if azure/login's 'creds' is used,
        # as 'DefaultAzureCredential' would be preferred and automatically pick up credentials.
        if tenant_id and client_id and client_secret:
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            # Attempt to get a token to verify the credential immediately
            credential.get_token("https://management.azure.com/.default")
            print("✅ ClientSecretCredential authentication successful.")
        else:
            print("⚠️ ClientSecretCredential details (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET) not fully available. Skipping ClientSecretCredential attempt.")
            # Raise an exception to fall through to DefaultAzureCredential
            raise ValueError("Incomplete ClientSecretCredential details.")

    except Exception as e:
        print(f"⚠️ ClientSecretCredential failed: {e}")
        print("Attempting DefaultAzureCredential...")
        try:
            credential = DefaultAzureCredential()
            # Attempt to get a token to verify the credential immediately
            credential.get_token("https://management.azure.com/.default")
            print("✅ DefaultAzureCredential authentication successful.")
        except Exception as inner_e:
            print(f"⚠️ DefaultAzureCredential failed: {inner_e}")
            # InteractiveBrowserCredential will not work in a non-interactive CI/CD environment
            print("Attempting InteractiveBrowserCredential (will only work locally with a browser and might cause issues in CI)...")
            credential = InteractiveBrowserCredential()

    # Ensure a credential object has been successfully obtained
    if credential is None:
        raise Exception("Failed to obtain any Azure credential for MLClient.")

    # Return MLClient initialized with the provided arguments
    return MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name
    )
