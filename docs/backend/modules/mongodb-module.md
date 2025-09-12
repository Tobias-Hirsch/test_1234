# `modules/mongodb_module.py` - MongoDB 数据库模块

本文档描述了 `backend/app/modules/mongodb_module.py` 文件，该文件封装了与 MongoDB 数据库交互的功能。

## 功能描述
*   **连接管理**: 提供 MongoDB 数据库的连接和客户端获取功能。
*   **文档操作**: 支持在 MongoDB 集合中插入、查询、更新和删除文档。
*   **集合管理**: 提供获取特定集合的引用。

## 逻辑实现
1.  **MongoDB 客户端**: 使用 `pymongo` 库的 `MongoClient` 类来创建 MongoDB 客户端实例，配置包括连接 URI。
    ```python
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure
    from backend.app.core.config import settings
    import logging

    logger = logging.getLogger(__name__)

    client: MongoClient = None

    def connect_to_mongodb():
        global client
        try:
            client = MongoClient(settings.MONGODB_URI)
            # The ping command is cheap and does not require auth.
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during MongoDB connection: {e}")
            raise

    def get_mongodb_client() -> MongoClient:
        if client is None:
            raise Exception("MongoDB client not initialized. Call connect_to_mongodb() first.")
        return client

    def get_database():
        return get_mongodb_client()[settings.MONGODB_DATABASE_NAME]

    def get_collection(collection_name: str):
        return get_database()[collection_name]
    ```
2.  **数据库和集合获取**: 提供函数来获取数据库实例和特定集合的引用，方便后续的 CRUD 操作。
3.  **CRUD 操作**: 虽然文件中没有直接展示所有 CRUD 函数，但通常会在此模块中实现或通过 `get_collection` 返回的 PyMongo 集合对象进行操作。例如：
    *   `insert_one(document)`
    *   `find_one(query)`
    *   `find(query)`
    *   `update_one(query, update)`
    *   `delete_one(query)`

## 路径
`/backend/app/modules/mongodb_module.py`