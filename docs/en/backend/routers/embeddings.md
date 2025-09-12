# `routers/embeddings.py` - Embeddings Routes

This document describes the `backend/app/routers/embeddings.py` file, which defines API routes related to text embedding generation.

## Function Description
*   **Generate Text Embeddings**: Provides an interface that allows clients to request the generation of vector embeddings for a given text.

## Logic Implementation
1.  **`create_embedding(text: str)`**:
    *   Receives the text for which to generate embeddings.
    *   Calls `rag_knowledge.embedding_service.get_text_embedding` to generate text embeddings.
    *   Returns the generated embedding vector.
    *   `@router.post("/embeddings")`

## Path
`/backend/app/routers/embeddings.py`