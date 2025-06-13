




# run_pipeline.py sdfdff
# sdfsfd

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
# lsflsdjjfjlk
# sfjsldfjlsdjlk sf
# sdfsjfl


from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential, ClientSecretCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment
from azure.core.exceptions import ResourceNotFoundError # Import for catching specific exception (though less critical for create_or_update)
# fjsldf

from src.config.connect import get_ml_client
import os
from src.config.connect import get_ml_client
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes

# --- Retrieve environment variables *inside* run_pipeline.py ---
# These variables are set by the 'env' block in your GitHub Actions workflow.
subscription_id = os.environ.get("SUBSCRIPTION_ID")
resource_group_name = os.environ.get("RESOURCE_GROUP_NAME")
workspace_name = os.environ.get("WORKSPACE_NAME")

# --- Add checks to ensure variables are present ---
if not all([subscription_id, resource_group_name, workspace_name]):
    missing_vars = [v for v, val in {"SUBSCRIPTION_ID": subscription_id, "RESOURCE_GROUP_NAME": resource_group_name, "WORKSPACE_NAME": workspace_name}.items() if val is None]
    raise ValueError(f"Missing one or more required Azure ML environment variables: {', '.join(missing_vars)}. Please ensure they are set in your GitHub workflow secrets and correctly passed to the 'Run Pipeline' step.")

# --- Initialize MLClient by passing the retrieved values ---
# This is the crucial change to resolve the TypeError
ml_client = get_ml_client(subscription_id, resource_group_name, workspace_name)
print("🎯 MLClient created successfully.")

def register_components(ml_client: MLClient, version: str):
    """Loads components from YAML and registers them with a unique version."""
    component_yamls = [
        "./component/create_environment/create_environment_component.yml",
        "./component/register_model/register_model_component.yml",
        "./component/deploy_model/deploy_model_component.yml",
    ]
    
    for comp_yaml in component_yamls:
        component = load_component(source=comp_yaml)
        component.version = version
        ml_client.components.create_or_update(component)
        print(f"Registered component '{component.name}' with version '{version}'")

@pipeline(
    default_compute="cpu-cluster", # Make sure this compute cluster exists in your workspace
    description="CI/CD pipeline to create env, register model, and deploy."
)
def model_cicd_pipeline(
    model_path: Input,
    model_name: str,
    endpoint_name: str,
    environment_base_name: str,
    conda_file: Input,
):
    """The definition of the CI/CD pipeline."""
    # These are loaded from the global scope within the main function
    create_env_comp = ml_client.components.get(name="create_environment", version=version)
    register_model_comp = ml_client.components.get(name="register_model", version=version)
    deploy_model_comp = ml_client.components.get(name="deploy_model", version=version)
    
    # Step 1: Create the environment
    create_env_step = create_env_comp(
        environment_name=environment_base_name,
        conda_file=conda_file
    )
    
    # Step 2: Register the model
    register_step = register_model_comp(
        model_path=model_path,
        model_name=model_name
    )
    
    # Step 3: Deploy the model
    deploy_step = deploy_model_comp(
        endpoint_name=endpoint_name,
        environment_name=create_env_step.outputs.created_env_name,
        environment_version=create_env_step.outputs.created_env_version,
        model_name=register_step.outputs.registered_model_name,
        model_version=register_step.outputs.registered_model_version
    )
    
    return {"deployment_status": deploy_step.outputs.deployment_status}

if __name__ == "__main__":
    ml_client = get_ml_client(subscription_id, resource_group_name, workspace_name)
    
    # Unique version for this run, e.g., based on timestamp or git commit hash
    version = datetime.now().strftime("%Y.%m.%d.%H%M%S")
    
    register_components(ml_client, version)
    
    pipeline_job = model_cicd_pipeline(
        model_path=Input(type='uri_file', path='./model/GBM_model_python_1749296476765_1.zip'), 
        model_name="my-h2o-cicd-model",
        endpoint_name="uddin", # Make sure this endpoint exists or will be created
        environment_base_name="iat-endpiont-v3",
        conda_file=Input(type='uri_file', path='./component/create_environment/conda.yaml')
    )
    
    pipeline_job.display_name = f"cicd-pipeline-{version}"
    
    submitted_job = ml_client.jobs.create_or_update(
        pipeline_job,
        experiment_name="cicd_pipeline_runs"
    )
    
    print("="*60)
    # nnn
    print(f"Pipeline job submitted. Name: {submitted_job.name}")
    print(f"View in Azure ML Studio: {submitted_job.studio_url}")
    print("="*60) 
   
