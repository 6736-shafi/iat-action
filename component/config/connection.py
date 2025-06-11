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

