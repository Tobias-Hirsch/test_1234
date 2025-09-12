import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
import io
import torch
import os
from pix2tex.cli import LatexOCR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Model Loading ---
# Global variable to hold the model
model = None

def load_model():
    """
    Loads the LatexOCR model based on the DEVICE environment variable.
    This function is called once at startup.
    """
    global model
    
    # Determine the device from an environment variable, defaulting to 'cpu'
    device = os.environ.get("DEVICE", "cpu").lower()
    if device == "cuda" and not torch.cuda.is_available():
        logger.warning("CUDA device requested but not available. Falling back to CPU.")
        device = "cpu"

    logger.info(f"Attempting to load LatexOCR model on device: '{device}'...")
    
    try:
        # The library will automatically use the available device (CUDA if possible)
        model = LatexOCR()
        logger.info(f"LatexOCR model loaded successfully on device '{device}'.")
    except Exception as e:
        logger.error(f"Failed to load LatexOCR model: {e}", exc_info=True)
        # If the model fails to load, the application should not start.
        raise RuntimeError("Could not initialize LatexOCR model.") from e

# --- FastAPI Application ---
app = FastAPI(
    title="Latex-OCR Service",
    description="A service to recognize mathematical formulas in images and return LaTeX code.",
)

@app.on_event("startup")
async def startup_event():
    """
    FastAPI startup event handler. Loads the model.
    """
    load_model()

@app.get("/", summary="Health Check")
async def read_root():
    """
    Root endpoint for health checks.
    """
    return {"status": "online", "model_loaded": model is not None}

@app.post("/predict", summary="Recognize LaTeX from Image")
async def predict(file: UploadFile = File(...)):
    """
    Receives an image file, processes it with the LatexOCR model,
    and returns the recognized LaTeX string.
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model is not available.")

    logger.info(f"Received request for file: {file.filename}")

    try:
        # Read image bytes from the uploaded file
        image_bytes = await file.read()
        img = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.error(f"Failed to read or open image file: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image file provided. Error: {e}")

    try:
        # Perform prediction
        # The model's __call__ method takes a PIL Image object
        latex_string = model(img)
        logger.info(f"Successfully recognized LaTeX for {file.filename}")
        return {"latex_string": latex_string}
    except Exception as e:
        logger.error(f"An error occurred during LaTeX recognition: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process image. Error: {e}")
