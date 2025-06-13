import os
from azure.ai.ml import MLClient
# from dotenv import load_dotenv # You might not need load_dotenv if all vars come from GitHub Actions

# If you use .env for local development, you might still keep this line:
# load_dotenv()

def get_ml_client():
    # Ensure these environment variables are correctly read
    subscription_id = os.environ.get("SUBSCRIPTION_ID")
    resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
    workspace_name = os.environ.get("WORKSPACE_NAME")

    if not all([subscription_id, resource_group_name, workspace_name]):
        raise ValueError("Azure ML workspace environment variables (SUBSCRIPTION_ID, RESOURCE_GROUP_NAME, WORKSPACE_NAME) are not set.")

    try:
        ml_client = MLClient(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            workspace_name=workspace_name
        )
        return ml_client
    except Exception as e:
        print(f"Error initializing MLClient: {e}")
        raise # Re-raise the exception after printing
