import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))

project_root = None
current_dir = script_dir
max_levels_up = 5

for _ in range(max_levels_up):
    if os.path.exists(os.path.join(current_dir, 'config')) and \
       os.path.exists(os.path.join(current_dir, 'component')):
        project_root = current_dir
        break
    parent_dir = os.path.dirname(current_dir)
    if parent_dir == current_dir:
        break
    current_dir = parent_dir

if project_root:
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
else:
    raise FileNotFoundError("Project root containing 'config' and 'component' folders not found. Please check your Azure ML job's file staging.")

from config.connect import get_ml_client

# Call your function here if needed
ml_client = get_ml_client()


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