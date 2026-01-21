from ultralytics import YOLO

def train():
    # Load a pre-trained model (nano version is fastest)
    model = YOLO("yolov8n.pt") 

    # Train the model
    # imgsz=640 is standard. 
    # epochs=20 is enough for a demo; use 50+ for best results.
    results = model.train(data="dataset.yaml", epochs=20, imgsz=640, name="pcb_defect_model")
    
    # Export the model for our backend to use
    model.export(format="torchscript")
    print("Training finished. Best model saved to 'runs/detect/pcb_defect_model/weights/best.pt'")

if __name__ == "__main__":
    train()