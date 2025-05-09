from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
import json
import os
from datetime import datetime

app = FastAPI(title="Heart Disease Detection API",
             description="API for analyzing heart X-ray images",
             version="1.0.0")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model yolları
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
MODEL_ARCHITECTURE = os.path.join(MODEL_DIR, "model_architecture.json")
MODEL_WEIGHTS = os.path.join(MODEL_DIR, "model_weights.h5")
CLASS_INDICES = os.path.join(MODEL_DIR, "class_indices.json")

# Model ve sınıf etiketlerini yükle
model = None
class_names = None

@app.on_event("startup")
async def load_model_and_classes():
    global model, class_names
    try:
        # Model mimarisini yükle
        with open(MODEL_ARCHITECTURE, 'r') as f:
            model_architecture = f.read()
        model = model_from_json(model_architecture)
        
        # Model ağırlıklarını yükle
        model.load_weights(MODEL_WEIGHTS)
        
        # Sınıf isimlerini yükle
        with open(CLASS_INDICES, 'r') as f:
            class_indices = json.load(f)
            class_names = {v: k for k, v in class_indices.items()}
            
    except Exception as e:
        raise RuntimeError(f"Model yüklenirken hata oluştu: {str(e)}")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, detail="Sadece resim dosyaları kabul edilir")
    
    try:
        # Resmi oku ve ön işleme yap
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        img = img.resize((224, 224))
        
        # Tahmin yap
        img_array = keras_image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0
        
        predictions = model.predict(img_array)
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = float(np.max(predictions[0]))
        
        return {
            "filename": file.filename,
            "prediction": predicted_class,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}