from ultralytics import YOLO

def build_edge_model():
    print("Downloading pre-trained YOLOv8 Nano...")
    model = YOLO("yolov8n.pt") 

    print("Exporting model to ONNX for edge deployment...")
    model.export(
        format="onnx", 
        dynamic=True,
        simplify=True,
        half=True
    )
    
    print("Success. 'yolov8n.onnx' is ready for deployment.")

if __name__ == "__main__":
    build_edge_model()
