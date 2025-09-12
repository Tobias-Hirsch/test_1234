# `modules/milvus_module.py` - Milvus 向量数据库模块

本文档描述了 `backend/app/modules/milvus_module.py` 文件，该文件封装了与 Milvus 向量数据库交互的功能。

## 功能描述
*   **连接管理**: 提供 Milvus 数据库的连接和断开功能。
*   **集合操作**: 支持创建、加载、释放和删除 Milvus 集合。
*   **数据插入**: 允许将向量数据和元数据插入到 Milvus 集合中。
*   **向量搜索**: 提供基于向量相似度的搜索功能。
*   **索引管理**: 支持为集合创建索引以优化搜索性能。

## 逻辑实现
1.  **Milvus 连接**: 使用 `pymilvus` 库的 `connections.connect` 方法建立与 Milvus 服务的连接，配置包括主机、端口和认证信息。
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
            # 检查并创建集合
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
                # 创建索引
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
        collection.load() # 确保集合已加载到内存
        return collection

    def release_milvus_collection():
        if utility.has_collection(settings.MILVUS_COLLECTION_NAME):
            collection = Collection(settings.MILVUS_COLLECTION_NAME)
            collection.release()
            logger.info(f"Collection '{settings.MILVUS_COLLECTION_NAME}' released.")
    ```
2.  **数据插入**: `Collection.insert` 方法用于将结构化数据（包括向量和元数据）插入到集合中。
3.  **向量搜索**: `Collection.search` 方法执行向量相似度搜索，根据查询向量找到最相似的文档块。
4.  **索引**: 通过 `collection.create_index` 为向量字段创建索引，例如 IVF_FLAT，以加速搜索操作。

## 路径
`/backend/app/modules/milvus_module.py`