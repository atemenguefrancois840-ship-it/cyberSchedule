import cv2
import numpy as np
import easyocr
import io
from PIL import Image
from fastapi import FastAPI, UploadFile, File

# Import des fonctions depuis ton engine.py
from engine import extraire_matieres_et_coeffs, parse_ocr_to_events

app = FastAPI(title="Titan OCR API")
reader = easyocr.Reader(['fr'], gpu=False)

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    img_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(gray)
    thresh = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

@app.post("/scan-schedule")
async def scan_schedule(file: UploadFile = File(...)):
    image_bytes = await file.read()
    processed_img = preprocess_image(image_bytes)
    ocr_results = reader.readtext(processed_img, detail=0)
    
    # 1. Transforme le texte OCR au format attendu par engine.py
    formatted_events = parse_ocr_to_events(ocr_results)
    
    # 2. Exécute ta logique métier
    matieres_coeffs, cours_par_jour = extraire_matieres_et_coeffs(formatted_events)
    
    return {
        "status": "success",
        "matieres_coeffs": matieres_coeffs,
        "cours_par_jour": cours_par_jour
    }
