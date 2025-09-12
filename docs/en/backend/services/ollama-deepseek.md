# `services/ollama_deepseek.py` - Ollama DeepSeek Integration Service

This document describes the `backend/app/services/ollama_deepseek.py` file, which may be specifically used to interact with the DeepSeek model deployed on a local Ollama service.

## Function Description
*   **DeepSeek Model Invocation**: Encapsulates the functionality to call the DeepSeek model on Ollama for text generation or chat completion.
*   **Specific Model Configuration**: May include parameter settings optimized for the DeepSeek model.

## Logic Implementation
This module will utilize general Ollama interaction functions defined in `ollama_module.py` and may add DeepSeek model-specific processing logic or parameters.

For example, an example of using the DeepSeek model for chat:
```python
import httpx
from backend.app.core.config import settings
from backend.app.modules.ollama_module import OLLAMA_BASE_URL
import logging

logger = logging.getLogger(__name__)

async def chat_with_ollama_deepseek(messages: list[dict], model_name: str = "deepseek-coder") -> str:
    """
    Interacts with the DeepSeek model via Ollama for chat completions.
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
        logger.error(f"Error connecting to Ollama DeepSeek service: {e}")
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama DeepSeek service returned an error: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during Ollama DeepSeek chat: {e}")
        raise
```

## Path
`/backend/app/services/ollama_deepseek.py`