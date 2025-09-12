import httpx
import logging
from fastapi import UploadFile, HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

async def call_paddleocr_service(file: UploadFile) -> dict | None:
    """
    Calls the external PaddleOCR service to perform OCR on a file.

    This function is responsible for sending a file to the dedicated PaddleOCR
    container and retrieving the structured OCR results.

    Args:
        file: The file to be processed, as an UploadFile object from FastAPI.

    Returns:
        A dictionary containing the OCR results, or None if an error occurred.
    """
    if not settings.PADDLEOCR_API_URL:
        logger.error("PADDLEOCR_API_URL is not configured in the environment.")
        raise HTTPException(status_code=500, detail="PaddleOCR service is not configured.")

    # Ensure the file pointer is at the beginning before reading
    await file.seek(0)
    
    # The full URL for the paddleocr service's OCR endpoint
    ocr_endpoint_url = f"{settings.PADDLEOCR_API_URL}/ocr"
    
    files = {'file': (file.filename, await file.read(), file.content_type)}
    
    # Use a long timeout to accommodate large files and slow processing
    timeout = httpx.Timeout(300.0) 
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            logger.info(f"Sending request to PaddleOCR service at {ocr_endpoint_url} for file: {file.filename}")
            response = await client.post(ocr_endpoint_url, files=files)
            
            # Raise an exception for 4xx (client) or 5xx (server) errors
            response.raise_for_status()
            
            logger.info(f"Received successful response from PaddleOCR service for file: {file.filename}")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            # Log specific HTTP errors from the service
            logger.error(f"PaddleOCR service returned an error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=502, detail=f"Error from PaddleOCR service: {e.response.text}")
        except httpx.RequestError as e:
            # Handle network-level errors (connection refused, timeout, etc.)
            logger.error(f"Could not connect to PaddleOCR service at {ocr_endpoint_url}. Error: {e}")
            raise HTTPException(status_code=503, detail="Could not connect to PaddleOCR service.")
        except Exception as e:
            # Catch any other unexpected errors
            logger.exception(f"An unexpected error occurred while calling PaddleOCR service for file {file.filename}.")
            raise HTTPException(status_code=500, detail="An unexpected error occurred.")
