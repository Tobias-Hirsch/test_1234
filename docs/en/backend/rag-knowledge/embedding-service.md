# `rag_knowledge/embedding_service.py` - Embedding Service

This document describes the `backend/app/rag_knowledge/embedding_service.py` file, which is responsible for generating text embeddings used for similarity search in vector databases (like Milvus).

## Function Description
*   **Text Embedding Generation**: Converts text into high-dimensional vectors using pre-trained models (e.g., OpenAI's `text-embedding-ada-002` or local Ollama models).
*   **Model Abstraction**: Encapsulates the calling logic for different embedding models, providing a unified interface.

## Logic Implementation
This module typically selects different embedding providers based on configuration.

For example, generating embeddings using OpenAI or Ollama:
```python
import os
from typing import List
from backend.app.core.config import settings
from backend.app.modules.ollama_module import generate_embedding_with_ollama
import logging

logger = logging.getLogger(__name__)

async def get_text_embedding(text: str) -> List[float]:
    """
    Generates an embedding for the given text using the configured embedding model.
    """
    if settings.OLLAMA_BASE_URL and settings.OLLAMA_EMBEDDING_MODEL:
        # Use Ollama for embeddings if configured
        try:
            embedding = await generate_embedding_with_ollama(settings.OLLAMA_EMBEDDING_MODEL, text)
            if not embedding:
                raise ValueError("Ollama embedding generation returned empty.")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding with Ollama: {e}")
            # Fallback to OpenAI if Ollama fails and OpenAI is configured
            if settings.OPENAI_API_KEY:
                logger.warning("Falling back to OpenAI for embedding generation.")
                return await _get_openai_embedding(text)
            else:
                raise
    elif settings.OPENAI_API_KEY:
        # Use OpenAI as the primary embedding provider
        return await _get_openai_embedding(text)
    else:
        raise ValueError("No embedding provider configured. Please set OLLAMA_BASE_URL/OLLAMA_EMBEDDING_MODEL or OPENAI_API_KEY.")

async def _get_openai_embedding(text: str) -> List[float]:
    """
    Generates an embedding using OpenAI's API.
    """
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.embeddings.create(
            input=text,
            model="text-embedding-ada-002" # Or other configured OpenAI embedding model
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding with OpenAI: {e}")
        raise
```

## Path
`/backend/app/rag_knowledge/embedding_service.py`