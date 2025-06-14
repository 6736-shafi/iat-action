import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from azure.ai.ml import MLClient

def get_ml_client() -> MLClient:
    print("--- Inside get_ml_client() ---")
    # Load environment variables from .env file for local development purposes.
    # In GitHub Actions, environment variables are set directly and override .env.
    # Temporarily comment out or modify load_dotenv for testing
    # load_dotenv() # <--- CONSIDER COMMENTING THIS OUT FOR GITHUB ACTIONS TESTING

    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    subscription_id = os.getenv("SUBSCRIPTION_ID")
    resource_group_name = os.getenv("RESOURCE_GROUP_NAME")
    workspace_name = os.getenv("WORKSPACE_NAME")

    print(f"Python sees TENANT_ID: {tenant_id}")
    print(f"Python sees CLIENT_ID: {client_id}")
    print(f"Python sees CLIENT_SECRET: {'*' * len(client_secret) if client_secret else 'None'}") # Mask
    print(f"Python sees SUBSCRIPTION_ID: {subscription_id}")
    print(f"Python sees RESOURCE_GROUP_NAME: {resource_group_name}")
    print(f"Python sees WORKSPACE_NAME: {workspace_name}")
    print("------------------------------")

    if not all([tenant_id, client_id, client_secret, subscription_id, resource_group_name, workspace_name]):
        raise ValueError(
            "One or more required environment variables (TENANT_ID, CLIENT_ID, CLIENT_SECRET, "
            "SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, WORKSPACE_NAME) are not set."
        )

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
