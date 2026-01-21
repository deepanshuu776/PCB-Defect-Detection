from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles # New import
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

# Allow the website to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
try:
    model = YOLO("model.pt")
except:
    model = YOLO("yolov8n.pt") # Fallback

def numpy_to_base64(image_np):
    img_pil = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    buff = BytesIO()
    img_pil.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

@app.post("/predict")
async def predict_defect(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model(img)
    
    detections = []
    for result in results:
        plotted_img = result.plot()
        for box in result.boxes:
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": box.xyxy.tolist()[0]
            })

    processed_image_b64 = numpy_to_base64(plotted_img)

    return JSONResponse({
        "status": "success",
        "defect_count": len(detections),
        "detections": detections,
        "image_base64": processed_image_b64
    })

# Serve the "static" folder as the website
app.mount("/", StaticFiles(directory="static", html=True), name="static")