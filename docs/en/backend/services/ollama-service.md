# `services/ollama_service.py` - Ollama General Service

This document describes the `backend/app/services/ollama_service.py` file, which may provide business logic for general interaction with the Ollama service, not limited to specific models.

## Function Description
*   **Ollama API Wrapper**: Encapsulates general calls to the Ollama REST API, such as listing models, pulling models, deleting models, etc.
*   **Health Check**: Checks if the Ollama service is available.
*   **General Text/Chat Interface**: Provides a general interface for text generation or chat completion with any model on Ollama.

## Logic Implementation
This module will directly or indirectly use the low-level HTTP client in `ollama_module.py` and provide higher-level business logic.

For example, a general Ollama chat service:
```python
import httpx
from backend.app.core.config import settings
from backend.app.modules.ollama_module import OLLAMA_BASE_URL
import logging

logger = logging.getLogger(__name__)

async def get_ollama_models() -> list[dict]:
    """Lists available models from Ollama service."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service to list models: {e}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred while listing Ollama models: {e}")
        return []

async def chat_with_ollama(messages: list[dict], model_name: str) -> str:
    """
    Interacts with a specified Ollama model for chat completions.
    Messages should be in the format: [{"role": "user", "content": "..."}]
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=600.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
    except httpx.RequestError as e:
        logger.error(f"Error connecting to Ollama service for chat: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama chat service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama chat: {e}")
        raise
```

## Path
`/backend/app/services/ollama_service.py`