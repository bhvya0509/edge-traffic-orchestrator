from roboflow import Roboflow

# Initialize with your PRIVATE API Key
rf = Roboflow(api_key="wn4LTKmegBbgTQiIenIX")

# Pulls the dataset
project = rf.workspace("amit-bd320").project("indian-vehicle-dataset-by-amit-juyal")
version = project.version(3)
dataset = version.download("yolov8")

print(f"Dataset successfully downloaded to: {dataset.location}")
