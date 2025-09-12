import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

import os

# The URL for the service, using the Docker service name for internal communication
# Get the service URL from environment variables, with a fallback to the default
LATEXOCR_SERVICE_URL = os.getenv("LATEXOCR_API_URL", "http://latexocr:8002/predict")

async def call_latexocr_service(image_bytes: bytes) -> Optional[str]:
    """
    Calls the Latex-OCR service to recognize a formula from image bytes.

    :param image_bytes: The raw bytes of the image file.
    :return: The recognized LaTeX string, or None if an error occurs.
    """
    logger.info("Sending image to Latex-OCR service for recognition.")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # The service expects a file upload, so we prepare the data accordingly.
            files = {'file': ('formula.png', image_bytes, 'image/png')}
            
            response = await client.post(LATEXOCR_SERVICE_URL, files=files)
            
            # Raise an exception for 4xx/5xx responses
            response.raise_for_status()
            
            data = response.json()
            latex_string = data.get("latex_string")
            
            if latex_string:
                logger.info("Successfully recognized LaTeX string from image.")
                return latex_string
            else:
                logger.warning("Latex-OCR service returned a response without a latex_string.")
                return None

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while calling Latex-OCR service: {e.response.status_code} - {e.response.text}")
            return None
        except httpx.RequestError as e:
            logger.error(f"Request error occurred while calling Latex-OCR service: {e}")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred in call_latexocr_service: {e}")
            return None
