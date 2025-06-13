import os
import sys


from config.connect import get_ml_client

# # Call your function here if needed
# ml_client = get_ml_client()

def add():
 
 
 return get_ml_client()
   
# from azure.ai.ml.entities import Model
# from azure.ai.ml.constants import AssetTypes
# model = Model(
#     path="./GBM_model_python_1749296476765_1.zip",  # Local model path
#     type=AssetTypes.CUSTOM_MODEL,
#     name="h2o-model",
#     description="My custom model registered from local file"
# )
# registered_model = ml_client.models.create_or_update(model)
# print(f"Model registered: {registered_model.name}, Version: {registered_model.version}")