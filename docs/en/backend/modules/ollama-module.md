# `modules/ollama_module.py` - Ollama Module

This document describes the `backend/app/modules/ollama_module.py` file, which may be used to interact with a locally running Ollama service to use local large language models.

## Function Description
*   **Ollama Connection**: Provides functionality to establish a connection with the Ollama service.
*   **Model Management**: May include functions to list available models, download models, etc.
*   **Text Generation**: Calls local models via the Ollama service for text generation.
*   **Embedding Generation**: Generates text embeddings via the Ollama service.

## Logic Implementation
This module typically uses the `httpx` or `requests` library to communicate with Ollama's REST API.

For example, a simple Ollama text generation example:
```python
import httpx
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

async def generate_text_with_ollama(model_name: str, prompt: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=600.0 # Increase timeout
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama text generation: {e}")
        raise

async def generate_embedding_with_ollama(model_name: str, text: str) -> list[float]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={
                    "model": model_name,
                    "prompt": text
                },
                timeout=600.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("embedding", [])
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service for embedding: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama embedding service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama embedding generation: {e}")
        raise
```

## Path
`/backend/app/modules/ollama_module.py`