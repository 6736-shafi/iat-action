import os
from datetime import datetime
from azure.ai.ml import MLClient, load_component, Input
from azure.ai.ml.dsl import pipeline
from azure.ai.ml.entities import CommandJob # For type hinting if needed, not directly instantiated here
from azure.ai.ml.constants import AssetTypes

# Import your custom connect module
from src.config.connect import get_ml_client # Adjusted path if necessary

# --- MLClient creation for pipeline submission (runs on GitHub Actions runner) ---s
# This block is essential for your run_pipeline.py to authenticate and submit to AML.
# The secrets are available in the GitHub Actions runner environment, so get_ml_client() here s
# should successfully retrieve them.
ml_client = None # Initialize to None
try:
    ml_client = get_ml_client()
    print("MLClient created successfully in run_pipeline.py (GitHub Actions runner context).")
except ValueError as e:
    print(f"Error creating MLClient in run_pipeline.py on GitHub Actions runner: {e}")
    # Exit the GitHub Actions job if the client can't be created
    exit(1)


# --- IMPORTANT: Retrieve environment variables from the GitHub Actions runner ---
# These are the variables that GitHub Actions is setting for run_pipeline.py.
# These will then be passed down to the Azure ML component runtimes.
env_vars_for_components = {
    "TENANT_ID": os.getenv("TENANT_ID"),
    "CLIENT_ID": os.getenv("CLIENT_ID"),
    "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
    "SUBSCRIPTION_ID": os.getenv("SUBSCRIPTION_ID"),
    "RESOURCE_GROUP_NAME": os.getenv("RESOURCE_GROUP_NAME"),
    "WORKSPACE_NAME": os.getenv("WORKSPACE_NAME")
}

# --- Debugging environment variables in run_pipeline.py itself ---
# This verifies what os.getenv() sees in the GitHub Actions Python process
print("\n--- Verifying raw OS environment in run_pipeline.py (GitHub Actions Python Process) ---")
print(f"os.getenv('TENANT_ID'): {os.getenv('TENANT_ID')}")
print(f"os.getenv('CLIENT_ID'): {os.getenv('CLIENT_ID')}")
print(f"os.getenv('CLIENT_SECRET'): {'*' * len(os.getenv('CLIENT_SECRET')) if os.getenv('CLIENT_SECRET') else 'None'}")
print(f"os.getenv('SUBSCRIPTION_ID'): {os.getenv('SUBSCRIPTION_ID')}")
print(f"os.getenv('RESOURCE_GROUP_NAME'): {os.getenv('RESOURCE_GROUP_NAME')}")
print(f"os.getenv('WORKSPACE_NAME'): {os.getenv('WORKSPACE_NAME')}")
print("------------------------------------------------------------------------------------\n")

# Assert that all variables are retrieved for passing to components
if not all(env_vars_for_components.values()):
    print("WARNING: One or more environment variables are None when collected in run_pipeline.py. Check GitHub Secrets.")
    # You might want to exit here if critical variables are missing
    # exit(1)



from src.utils.get_model_path import get_latest_model_from_folder

from src.config.connect import get_ml_client


def register_components(client: MLClient, version_str: str):
    """Loads components from YAML and registers them with a unique version."""
    component_yamls = [
        "./component/create_environment/create_environment_component.yml",
        "./component/register_model/register_model_component.yml",
        "./component/deploy_model/deploy_model_component.yml",
    ]

    for comp_yaml in component_yamls:
        component = load_component(source=comp_yaml)
        component.version = version_str # Use the passed version string
        client.components.create_or_update(component)
        print(f"Registered component '{component.name}' with version '{version_str}'")


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
    # These are loaded from the global scope using the ml_client created above
    # Make sure 'version' is accessible here (e.g., passed as an argument or from global scope)
    global ml_client, version # Access global ml_client and version
    
    create_env_comp = ml_client.components.get(name="create_environment", version=version)
    register_model_comp = ml_client.components.get(name="register_model", version=version)
    deploy_model_comp = ml_client.components.get(name="deploy_model", version=version)

    # Step 1: Create the environment
    create_env_step = create_env_comp(
        environment_name=environment_base_name,
        conda_file=conda_file
    )
    # THIS IS THE CRUCIAL PART FOR PASSING ENV VARS TO THE COMPONENT'S RUNTIME
    create_env_step.environment_variables = env_vars_for_components
    print(f"\n--- Debugging create_env_step.environment_variables (in run_pipeline.py) ---")
    print(f"Type: {type(create_env_step.environment_variables)}")
    print(f"Value: {create_env_step.environment_variables}")
    print("----------------------------------------------------------------------------")


    # Step 2: Register the model
    register_step = register_model_comp(
        model_path=model_path,
        model_name=model_name
    )
    # THIS IS THE CRUCIAL PART FOR PASSING ENV VARS TO THE COMPONENT'S RUNTIME
    register_step.environment_variables = env_vars_for_components
    print(f"\n--- Debugging register_step.environment_variables (in run_pipeline.py) ---")
    print(f"Type: {type(register_step.environment_variables)}")
    print(f"Value: {register_step.environment_variables}")
    print("--------------------------------------------------------------------------")


    # Step 3: Deploy the model
    deploy_step = deploy_model_comp(
        endpoint_name=endpoint_name,
        environment_name=create_env_step.outputs.created_env_name,
        environment_version=create_env_step.outputs.created_env_version,
        model_name=register_step.outputs.registered_model_name,
        model_version=register_step.outputs.registered_model_version
    )
    # THIS IS THE CRUCIAL PART FOR PASSING ENV VARS TO THE COMPONENT'S RUNTIME
    deploy_step.environment_variables = env_vars_for_components
    print(f"\n--- Debugging deploy_step.environment_variables (in run_pipeline.py) ---")
    print(f"Type: {type(deploy_step.environment_variables)}")
    print(f"Value: {deploy_step.environment_variables}")
    print("-------------------------------------------------------------------------")

    return {"deployment_status": deploy_step.outputs.deployment_status}

if __name__ == "__main__":
    ml_client = get_ml_client()
    latest_model = get_latest_model_from_folder('./model')
    print(f"Latest model found: {latest_model}")
    latest_model='./model/'+latest_model
    
    
    
    # Unique version for this run, e.g., based on timestamp or git commit hash
    version = datetime.now().strftime("%Y.%m.%d.%H%M%S")
    
    register_components(ml_client, version)
    
    pipeline_job = model_cicd_pipeline(
        model_path=Input(type='uri_file', path=latest_model),
        model_name="my-h2o-cicd-model",

        endpoint_name="shafi", # Make sure this endpoint exists or will be created!s

        environment_base_name="iat-endpoint-v3", # Corrected typo "endpiont" to "endpoint"
        conda_file=Input(type=AssetTypes.URI_FILE, path='./component/create_environment/conda.yaml')
    )
    
    pipeline_job.display_name = f"cicd-pipeline-{version}"
    
    submitted_job = ml_client.jobs.create_or_update(
        pipeline_job,
        experiment_name="cicd_pipeline_runs"
    )
    
    print("="*60)
    print(f"Pipeline job submitted. Name: {submitted_job.name}")
    print(f"View in Azure ML Studio: {submitted_job.studio_url}")
    print("="*60) 
   


# from src.utils.get_model_path import get_latest_model_from_folder

# latest_model = get_latest_model_from_folder('./model')
# print(f"Latest model found: {latest_model}")
# latest_model='./model/'+latest_model
# print(f"Full path to latest model: {latest_model}")
