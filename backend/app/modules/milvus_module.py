import os
from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType, IndexType
from typing import List, Dict, Any
from app.rag_knowledge.embedding_service import EmbeddingService # Import EmbeddingService
import asyncio # Import asyncio for running async functions
from ..core.config import settings # Global import

MILVUS_HOST = settings.MILVUS_HOST
MILVUS_PORT = settings.MILVUS_PORT
MILVUS_COLLECTION_NAME = settings.MILVUS_COLLECTION_NAME
VECTOR_DIM = settings.VECTOR_DIM  # Use VECTOR_DIM from .env, default to 1024

def get_milvus_collection(collection_name: str = MILVUS_COLLECTION_NAME) -> Collection:
    """Connects to Milvus and returns the specified collection."""
    connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
    collection = Collection(collection_name)
    if not collection.is_loaded:
        collection.load()
    return collection

async def generate_embedding(text: str) -> List[float]:
    """
    Generates an embedding for the given text using the configured Ollama embedding model.
    """
    embedding_service = EmbeddingService()
    ollama_embedding_model = settings.OLLAMA_EMBEDDING_MODEL
    print(f"DEBUG: Attempting to get embedding for text (first 50 chars): {text[:50]}... using model: {ollama_embedding_model}")
    embedding = await embedding_service.get_embedding(text, model=ollama_embedding_model)
    
    if embedding is not None:
        print(f"DEBUG: Successfully generated embedding. Shape: {embedding.shape}, Type: {type(embedding)}")
        return embedding.tolist() # Convert numpy array to list for Milvus
    else:
        print(f"ERROR: Failed to generate embedding for text: {text[:50]}... Embedding is None.")
        print(f"DEBUG: VECTOR_DIM = {VECTOR_DIM}")
        # Ensure VECTOR_DIM is a positive integer before creating a zero vector
        if isinstance(VECTOR_DIM, int) and VECTOR_DIM > 0:
            return [0.0] * VECTOR_DIM # Return a zero vector or handle error as appropriate
        else:
            print(f"CRITICAL ERROR: VECTOR_DIM is invalid ({VECTOR_DIM}). Cannot return zero vector.")
            raise ValueError("VECTOR_DIM is not a positive integer, cannot generate zero vector.")