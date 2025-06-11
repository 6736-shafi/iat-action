from datetime import datetime
from azure.ai.ml import MLClient, load_component, Input
from azure.ai.ml.dsl import pipeline
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential

def get_ml_client():
    """Authenticates and returns an MLClient."""
    try:
        credential = DefaultAzureCredential()
        credential.get_token("https://management.azure.com/.default")
    except Exception:
        credential = InteractiveBrowserCredential()
    
    return MLClient(
        credential=credential,
        subscription_id="6bd1f99e-e7cb-4226-b9d5-09433d793bda",
        resource_group_name="shafi1",
        workspace_name="shafi1"
    )

def register_components(ml_client: MLClient):
    """Loads components from YAML and registers them with a unique version."""
    # Create a unique version string for this run
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    
    component_yamls = [
        "./component/register_model/register_model_component.yml",
        "./component/deploy_model/deploy_model_component.yml"
    ]
    
    for comp_yaml in component_yamls:
        component = load_component(source=comp_yaml)
        component.version = version
        ml_client.components.create_or_update(component)
        print(f"Registered component '{component.name}' with version '{version}'")
        
    return version

@pipeline(
    default_compute="cpu-cluster",
    description="CI/CD pipeline to register and deploy a model."
)
def model_cicd_pipeline(
    model_path: Input,
    model_name: str,
    endpoint_name: str,
    environment_name: str,
    environment_version: str
):
    """The definition of the CI/CD pipeline."""
    # Note: This approach requires 'ml_client' and 'version' to be accessible in the global scope
    # where this pipeline function is called.
    register_model_comp = ml_client.components.get(name="register_model", version=version)
    deploy_model_comp = ml_client.components.get(name="deploy_model", version=version)
    
    # Step 1: Register the model
    register_step = register_model_comp(
        model_path=model_path,
        model_name=model_name
    )
    
    # Step 2: Deploy the model, using outputs from the registration step
    deploy_step = deploy_model_comp(
        endpoint_name=endpoint_name,
        environment_name=environment_name,
        environment_version=environment_version,
        model_name=register_step.outputs.registered_model_name,
        model_version=register_step.outputs.registered_model_version
    )
    
    return {
        "deployment_status": deploy_step.outputs.deployment_status
    }

if __name__ == "__main__":
    ml_client = get_ml_client()
    
    # Register components with a new version for this run
    version = register_components(ml_client)
    
    # Define the pipeline using the new component version
    pipeline_job = model_cicd_pipeline(
        model_path=Input(type='uri_file', path='./GBM_model_python_1749296476765_1.zip'), 
        model_name="my-h2o-cicd-model",
        endpoint_name="shafi1",
        environment_name="h2o-env",
        environment_version="3"
    )
    
    # Give the pipeline job a unique name
    pipeline_job.display_name = f"cicd-pipeline-{version}"
    
    # Submit the pipeline job
    submitted_job = ml_client.jobs.create_or_update(
        pipeline_job,
        experiment_name="cicd_pipeline_runs"
    )
    
    print(f"Pipeline job submitted. View in Azure ML Studio: {submitted_job.studio_url}")
