# `modules/milvus_module.py` - Milvus Vector Database Module

This document describes the `backend/app/modules/milvus_module.py` file, which encapsulates functionalities for interacting with the Milvus vector database.

## Function Description
*   **Connection Management**: Provides functions for connecting to and disconnecting from the Milvus database.
*   **Collection Operations**: Supports creating, loading, releasing, and deleting Milvus collections.
*   **Data Insertion**: Allows inserting vector data and metadata into Milvus collections.
*   **Vector Search**: Provides vector similarity-based search functionality.
*   **Index Management**: Supports creating indexes for collections to optimize search performance.

## Logic Implementation
1.  **Milvus Connection**: Establishes a connection to the Milvus service using the `connections.connect` method from the `pymilvus` library, with configuration including host, port, and authentication information.
    ```python
    from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
    from backend.app.core.config import settings
    import logging

    logger = logging.getLogger(__name__)

    async def connect_to_milvus():
        try:
            connections.connect(
                alias="default",
                host=settings.MILVUS_HOST,
                port=settings.MILVUS_PORT
            )
            logger.info(f"Successfully connected to Milvus at {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            # Check and create collection
            if not utility.has_collection(settings.MILVUS_COLLECTION_NAME):
                fields = [
                    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.MILVUS_VECTOR_DIM),
                    FieldSchema(name="filename", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="chunk_id", dtype=DataType.INT64),
                    FieldSchema(name="chunk_content", dtype=DataType.TEXT),
                    FieldSchema(name="summary", dtype=DataType.TEXT),
                    FieldSchema(name="download_url", dtype=DataType.VARCHAR, max_length=1024)
                ]
                schema = CollectionSchema(fields, "Rosti RAG Collection for document embeddings")
                collection = Collection(settings.MILVUS_COLLECTION_NAME, schema)
                # Create index
                index_params = {
                    "metric_type": "COSINE",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
                collection.create_index(field_name="embedding", index_params=index_params)
                logger.info(f"Collection '{settings.MILVUS_COLLECTION_NAME}' created and indexed successfully.")
            else:
                logger.info(f"Collection '{settings.MILVUS_COLLECTION_NAME}' already exists.")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus or create collection: {e}")
            raise

    def get_milvus_collection() -> Collection:
        if not utility.has_collection(settings.MILVUS_COLLECTION_NAME):
            raise Exception(f"Milvus collection '{settings.MILVUS_COLLECTION_NAME}' does not exist.")
        collection = Collection(settings.MILVUS_COLLECTION_NAME)
        collection.load() # Ensure the collection is loaded into memory
        return collection

    def release_milvus_collection():
        if utility.has_collection(settings.MILVUS_COLLECTION_NAME):
            collection = Collection(settings.MILVUS_COLLECTION_NAME)
            collection.release()
            logger.info(f"Collection '{settings.MILVUS_COLLECTION_NAME}' released.")
    ```
2.  **Data Insertion**: The `Collection.insert` method is used to insert structured data (including vectors and metadata) into the collection.
3.  **Vector Search**: The `Collection.search` method performs vector similarity search, finding the most similar document chunks based on the query vector.
4.  **Indexing**: Indexes, such as IVF_FLAT, are created for vector fields via `collection.create_index` to accelerate search operations.

## Path
`/backend/app/modules/milvus_module.py`