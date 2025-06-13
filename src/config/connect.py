import os
from dotenv import load_dotenv
from datetime import datetime
from azure.identity import (
    DefaultAzureCredential,
    InteractiveBrowserCredential,
    ClientSecretCredential
)
from azure.ai.ml import MLClient
from azure.ai.ml.dsl import pipeline
from azure.core.exceptions import ClientAuthenticationError

# Load environment variables from .env file
load_dotenv()

def get_ml_client():
    """
    Authenticates and returns an MLClient using environment variables.
    Falls back to DefaultAzureCredential and then InteractiveBrowserCredential if needed.
    """

    tenant_id = os.getenv("TENANT_ID")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    subscription_id = os.getenv("SUBSCRIPTION_ID")
    resource_group_name = os.getenv("RESOURCE_GROUP_NAME")
    workspace_name = os.getenv("WORKSPACE_NAME")

    credential = None

    print("Trying authentication with Service Principal credentials...")
    try:
        credential = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        credential.get_token("https://management.azure.com/.default")
        print("✅ Service Principal authentication successful.")
    except Exception as e:
        print(f"⚠️  Service Principal authentication failed: {e}")
        print("Attempting DefaultAzureCredential...")
        try:
            credential = DefaultAzureCredential()
            credential.get_token("https://management.azure.com/.default")
            print("✅ DefaultAzureCredential authentication successful.")
        except Exception as inner_e:
            print(f"⚠️  DefaultAzureCredential failed: {inner_e}")
            print("Attempting InteractiveBrowserCredential...")
            credential = InteractiveBrowserCredential()

    # Return MLClient
    return MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name
    )

ml_client= get_ml_client()
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes
model = Model(
    path="./GBM_model_python_1749296476765_1.zip",  # Local model path
    type=AssetTypes.CUSTOM_MODEL,
    name="h2o-model",
    description="My custom model registered from local file"
)
registered_model = ml_client.models.create_or_update(model)
print(f"Model registered: {registered_model.name}, Version: {registered_model.version}")

# # Example usage
# if __name__ == "__main__":
#     try:
#         ml_client = get_ml_client()
#         print("🎯 MLClient created successfully.")
#     except ClientAuthenticationError as e:
#         print(f"❌ Authentication failed: {e}")


# from azure.ai.ml import MLClient
# from azure.identity import DefaultAzureCredential, ClientSecretCredential
# import os

# def get_ml_client():
#     try:
#         # Try default credential (works well in CI/CD or when logged in via Azure CLI)
#         ml_client = MLClient.from_config(credential=DefaultAzureCredential())
#     except Exception as ex:
#         print(f"DefaultAzureCredential failed: {ex}")
#         print("Falling back to ClientSecretCredential...")

#         # Fallback to explicit Service Principal credentials
#         ml_client = MLClient(
#             credential=ClientSecretCredential(
#                 tenant_id=os.environ["AZURE_TENANT_ID"],
#                 client_id=os.environ["AZURE_CLIENT_ID"],
#                 client_secret=os.environ["AZURE_CLIENT_SECRET"]
#             ),
#             subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
#             resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
#             workspace_name=os.environ["AZURE_WORKSPACE_NAME"]
#         )

#     print(f"✅ Logged in to Azure ML workspace: {ml_client.workspace_name}")
#     return ml_client
# get_ml_client = get_ml_client()
