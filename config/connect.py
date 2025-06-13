# run_pipeline.py
import os
from datetime import datetime
from azure.ai.ml import MLClient, load_component, Input
from azure.ai.ml.dsl import pipeline

from azure.identity import DefaultAzureCredential

import os
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
import argparse
import sys
from pathlib import Path
import os


from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, ClientSecretCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment
from azure.core.exceptions import ResourceNotFoundError # Import for catching specific exception (though less critical for create_or_update)


def get_ml_client():
    """
    Authenticates and returns an MLClient.
    Prioritizes ClientSecretCredential (for service principal) with hardcoded values,
    otherwise falls back to DefaultAzureCredential.
    """
    # --- WARNING: HARDCODING CREDENTIALS IS NOT RECOMMENDED FOR PRODUCTION ---
    # This is for temporary testing only. For secure applications, use environment variables
    # or Azure Key Vault to manage secrets.

    tenant_id = "084a029e-1435-40bc-8201-87ec1b251fb3"
    client_id = "bd13c2e3-28bc-4e29-bc12-1d2461071a68"
    client_secret = "5lO8Q~1IFYUOtQff0rGSBKgwJD3L-6GX3AFOKank"


    # Your Azure subscription, resource group, and workspace details
    subscription_id = "6bd1f99e-e7cb-4226-b9d5-09433d793bda"
    resource_group_name = "shafi1"
    workspace_name = "shafi1"

    # Use ClientSecretCredential with the hardcoded values
    print("Attempting authentication with hardcoded Service Principal credentials...")
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    # The DefaultAzureCredential fallback path is now less likely to be hit,
    # but the structure remains if you decide to uncomment it later.
    try:
        # Attempt to get a token to verify the hardcoded credentials
        credential.get_token("https://management.azure.com/.default")
        print("Hardcoded Service Principal authentication successful.")
    except Exception as e:
        print(f"Hardcoded Service Principal authentication failed: {e}.")
        print("Falling back to DefaultAzureCredential (which may prompt for interactive login if no other credentials are found)...")
        try:
            credential = DefaultAzureCredential()
            credential.get_token("https://management.azure.com/.default")
            print("DefaultAzureCredential successful.")
        except Exception as inner_e:
            print(f"DefaultAzureCredential also failed: {inner_e}. Falling back to InteractiveBrowserCredential...")
            credential = InteractiveBrowserCredential()


    # Initialize MLClient
    return MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        workspace_name=workspace_name
    )